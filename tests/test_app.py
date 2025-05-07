"""Pytest test‑suite for the Veteran‑Transition‑Center‑Project.

Run with:

    pytest -q

The suite spins up the real Flask application object (using the same
`create_app()` factory that *run.py* uses) but points SQLAlchemy at an
**in‑memory SQLite database** so nothing on disk is touched.
"""

# ---------------------------------------------------------------------------
#  Necessary path tweak so that `import app` works when the repo root is the
#  current working directory (the normal case when you just type `pytest`).
# ---------------------------------------------------------------------------

import pathlib
import sys
from decimal import Decimal

# Ensure the repository root (parent of this tests/ directory) is on sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Now we can import the real application package
from app import create_app, db

import pytest
from flask import current_app

from app.models import (
    ProgramModel,
    CostsPerProgramModel,
    DailyEntriesModel,
    TotalModel,
)


# ---------------------------------------------------------------------------
#  Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """Create the Flask app *configured for tests* and open an app‑context."""

    test_app = create_app()

    # Point SQLAlchemy at an in‑memory DB **before** anything touches the DB.
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with test_app.app_context():
        db.drop_all()
        db.create_all()

        yield test_app

        # Teardown — clean up the DB and context
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """A handy Flask test‑client."""
    return app.test_client()


@pytest.fixture()
def sample_data(app):
    """Seed baseline data used by several tests."""
    with app.app_context():
        program_a = ProgramModel(name="Program A", rate=Decimal("50.25"))
        program_b = ProgramModel(name="Program B", rate=Decimal("75.40"))
        db.session.add_all([program_a, program_b])

        salary = CostsPerProgramModel(program_id=program_a.id, salary=Decimal("0"))
        db.session.add(salary)
        db.session.commit()

        yield {
            "programs": [program_a, program_b],
        }


# ---------------------------------------------------------------------------
#  Helper
# ---------------------------------------------------------------------------

def _post_daily_totals(client, counts):
    """POST to /add_daily_totals with the given list of participant counts."""
    data = [("number_of_participants", str(c)) for c in counts]
    return client.post("/add_daily_totals", data=data, follow_redirects=False)


# ---------------------------------------------------------------------------
#  Test cases
# ---------------------------------------------------------------------------

def test_daily_post_creates_entries_and_total(client, sample_data):
    """Posting counts should create DailyEntries rows and a Total row."""

    resp = _post_daily_totals(client, [2, 3])  # 2×50.25 + 3×75.40 = 326.70
    assert resp.status_code == 302  # route redirects back to index

    with current_app.app_context():
        entries = DailyEntriesModel.query.all()
        assert len(entries) == 2
        assert {e.number_of_participants for e in entries} == {2, 3}

        total = TotalModel.query.first()
        assert Decimal(total.grand_total) == Decimal("326.70")


def test_second_post_accumulates(client, sample_data):
    """A second POST should add on to the running grand_total."""

    _post_daily_totals(client, [1, 1])  # 125.65
    with current_app.app_context():
        first = Decimal(TotalModel.query.first().grand_total)
        assert first == Decimal("125.65")

    _post_daily_totals(client, [0, 2])  # +150.80

    with current_app.app_context():
        totals = TotalModel.query.order_by(TotalModel.id.asc()).all()
        assert len(totals) == 2
        assert Decimal(totals[1].grand_total) == Decimal("276.45")


def test_amount_nullable(client, app):
    """Direct insert with amount=None should succeed if column is nullable."""

    with app.app_context():
        row = TotalModel(grand_total=0, comment="null‑amount", entry_date=None, amount=None)
        db.session.add(row)
        db.session.commit()

        fetched = TotalModel.query.filter_by(comment="null‑amount").first()
        assert fetched.amount is None