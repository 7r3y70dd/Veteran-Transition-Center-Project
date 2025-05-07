# from .models import User
from datetime import timedelta, datetime
from decimal import Decimal
from . import db
from flask import render_template, request, redirect, url_for, Blueprint
from .models import CostsPerProgramModel, ProgramModel, DailyEntriesModel, TotalModel
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    latest_total = TotalModel.query.order_by(TotalModel.id.desc()).first()

    return render_template('index.html', total=round(latest_total.grand_total, 2))

@main.route('/add_data')
def add_data():
    return render_template('add_data.html')

@main.route('/add_delete_support_staff', methods=['GET', 'POST'])
def add_delete_support_staff():
    if request.method == 'POST':
        program_name = request.form['program_name']
        employee_name = request.form['employee_name']
        salary = float(request.form['salary'])
        action = request.form['action']  # Action to determine if we're adding or deleting

        program = ProgramModel.query.filter_by(name=program_name).first()

        if program:
            if action == 'add':
                new_support_staff = CostsPerProgramModel(
                    program_id=program.id,
                    salary=salary,
                    name=employee_name
                )
                db.session.add(new_support_staff)
                db.session.commit()
                return redirect(url_for('main.index'))

            elif action == 'delete':
                staff_to_delete = CostsPerProgramModel.query.filter_by(
                    program_id=program.id,
                    salary=salary,
                    name=employee_name
                ).first()

                if staff_to_delete:
                    db.session.delete(staff_to_delete)
                    db.session.commit()

                return redirect(url_for('main.index'))

        else:
            return "Program not found", 404

    all_programs = ProgramModel.query.order_by(ProgramModel.name).all()
    return render_template("add_delete_support_staff.html", programs=all_programs)

@main.route('/veiw_data')
def view_data():
    return render_template('view_data.html')


@main.route('/add_delete_program', methods=['GET', 'POST'])
def add_delete_program():
    if request.method == 'POST':
        program_name = request.form['program_name']
        rate = float(request.form['rate'])
        action = request.form['action']  # Action to determine if we're adding or deleting

        if action == 'add':
            new_program = ProgramModel(program_name=program_name, rate=rate)

            db.session.add(new_program)
            db.session.commit()
            return redirect(url_for('main.index'))  # Redirect to the index or another page

        elif action == 'delete':
            program_to_delete = ProgramModel.query.filter_by(name=program_name, rate=rate).first()

            if program_to_delete:
                db.session.delete(program_to_delete)
                db.session.commit()

            return redirect(url_for('main.index'))  # Redirect after deletion

    return render_template('add_delete_program.html')

# @main.route('/add_daily_totals', methods=['GET', 'POST'])
# def add_daily_totals():
#     if request.method == 'POST':
#         from datetime import datetime
#
#
#         entries = request.form.getlist('number_of_participants')
#         entry_date = datetime.now()  # Use current datetime directly
#
#         # entries = request.form.getlist('number_of_participants')
#         # entry_date_str = request.form['date']
#         # entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d')
#
#         daily_total = Decimal("0")
#
#         for i, program in enumerate(ProgramModel.query.all()):
#             number_of_participants = int(entries[i]) if entries[i] else 0
#             program_rate = program.rate
#
#             # Calculate this program's contribution to the daily total
#             daily_total += number_of_participants * program_rate
#
#             print(f"Checking for existing entry - Program ID: {program.id}, Date: {entry_date}")
#
#             # Check if a daily entry already exists
#             existing_entry = DailyEntriesModel.query.filter_by(
#                 program_id=program.id,
#                 date=entry_date.date()
#             ).first()
#
#             if existing_entry:
#                 existing_entry.number_of_participants = number_of_participants
#             else:
#                 print(f"No existing entry found for Program ID {program.id} on {entry_date}, will create a new one.")
#                 new_entry = DailyEntriesModel(
#                     number_of_participants=number_of_participants,
#                     program_id=program.id,
#                     date=entry_date
#                 )
#                 db.session.add(new_entry)
#
#
#         # After processing all programs, save the total
#         # existing_total = TotalModel.query.filter_by(
#         #     date=entry_date.date(),
#         #     # comment='program numbers entry'
#         # ).first()
#         existing_total = TotalModel.query.filter(
#             func.date(TotalModel.date) == entry_date.date(),
#             TotalModel.comment == 'program numbers entry'
#         ).order_by(TotalModel.date.desc()).first()
#
#         cutoff_date = entry_date.date() - timedelta(days=1)
#
#         prior_entry = TotalModel.query.filter(
#             TotalModel.date <= cutoff_date
#         ).order_by(TotalModel.date.desc()).first()
#
#         previous_grand_total = prior_entry.grand_total if prior_entry is not None and prior_entry.grand_total is not None else Decimal("0")
#
#         updated_grand_total = previous_grand_total + daily_total
#
#         if existing_total:
#             existing_total.grand_total = updated_grand_total
#
#             subsequent_entries = TotalModel.query.filter(
#                 TotalModel.date > existing_total.date,
#                 TotalModel.comment != 'program numbers entry'
#             ).order_by(TotalModel.date.asc()).all()
#
#             running_total = existing_total.grand_total
#
#             print('starting total edited: ' + str(running_total))
#
#             for entry in subsequent_entries:
#                 print('start runn  ' + str(running_total))
#                 print('entry:  ' + str(entry.grand_total))
#                 running_total = running_total - entry.amount
#                 entry.grand_total = running_total
#         else:
#             # Get the most recent total from the TotalModel table (if any)
#             last_total_entry = TotalModel.query.order_by(TotalModel.id.desc()).first()
#             last_grand_total = last_total_entry.grand_total if last_total_entry else 0.0
#
#             # Add the current daily total to the last grand total
#             combined_total = daily_total + last_grand_total
#
#             total_annual_salary = db.session.query(
#                 db.func.sum(CostsPerProgramModel.salary)
#             ).scalar() or 0.0
#             daily_salary_cost = total_annual_salary / 365
#
#             final_total = combined_total - daily_salary_cost
#
#             # Create the new entry
#             new_total = TotalModel(
#                 grand_total=final_total,
#                 comment='program numbers entry',
#                 entry_date=datetime.now()
#             )
#             db.session.add(new_total)
#
#         db.session.commit()
#         return redirect(url_for('main.index'))
#
#     # If the request method is GET, render the form
#     programs = ProgramModel.query.all()
#     last_entries = {}
#
#     # Get the last entry for each program (not strictly necessary anymore)
#     for program in programs:
#         last_entry = DailyEntriesModel.query.filter_by(program_id=program.id).order_by(DailyEntriesModel.date.desc()).first()
#         last_entries[program.id] = last_entry.number_of_participants if last_entry else 0
#
#     return render_template('add_daily_totals.html', programs=programs, last_entries=last_entries)

@main.route("/add_daily_totals", methods=["GET", "POST"])
def add_daily_totals():
    if request.method == "POST":
        entries = request.form.getlist("number_of_participants")
        entry_date = datetime.now()

        daily_total = Decimal("0")

        for i, program in enumerate(ProgramModel.query.all()):
            number_of_participants = int(entries[i]) if entries[i] else 0
            program_rate = program.rate                              # Decimal

            contribution = number_of_participants * program_rate
            print(
                f"participants: {number_of_participants} * "
                f"rate: {program_rate} -----> contribution: {contribution}"
            )


            before = daily_total
            daily_total += contribution
            print(
                f"daily_total(prev): {before} + contribution: {contribution} "
                f"-----> daily_total: {daily_total}"
            )

            existing_entry = DailyEntriesModel.query.filter_by(
                program_id=program.id,
                date=entry_date.date()
            ).first()

            if existing_entry:
                existing_entry.number_of_participants = number_of_participants
            else:
                new_entry = DailyEntriesModel(
                    number_of_participants=number_of_participants,
                    program_id=program.id,
                    date=entry_date
                )
                db.session.add(new_entry)

        existing_total = TotalModel.query.filter(
            func.date(TotalModel.date) == entry_date.date(),
            TotalModel.comment == "program numbers entry"
        ).order_by(TotalModel.date.desc()).first()

        cutoff_date = entry_date.date() - timedelta(days=1)

        prior_entry = TotalModel.query.filter(
            TotalModel.date <= cutoff_date
        ).order_by(TotalModel.date.desc()).first()

        previous_grand_total = (
            prior_entry.grand_total
            if prior_entry is not None and prior_entry.grand_total is not None
            else Decimal("0")
        )

        updated_grand_total = previous_grand_total + daily_total

        print(
            f"previous_grand_total: {previous_grand_total} + "
            f"daily_total: {daily_total} -----> "
            f"updated_grand_total: {updated_grand_total}"
        )

        if existing_total:
            total_annual_salary = db.session.query(
                db.func.sum(CostsPerProgramModel.salary)
            ).scalar() or Decimal("0")

            daily_salary_cost = total_annual_salary / 365

            existing_total.grand_total = updated_grand_total - daily_salary_cost

            subsequent_entries = TotalModel.query.filter(
                TotalModel.date > existing_total.date,
                TotalModel.comment != "program numbers entry"
            ).order_by(TotalModel.date.asc()).all()

            running_total = existing_total.grand_total

            print(
                f"combined_total: {existing_total.grand_total} - "
                f"daily_salary_cost: {daily_salary_cost} -----> "
                f"final_total: {running_total}"
            )

            for entry in subsequent_entries:
                before = running_total
                running_total = running_total - entry.amount
                print(
                    f"running_total(prev): {before} - "
                    f"entry.amount: {entry.amount} -----> "
                    f"running_total: {running_total}"
                )
                entry.grand_total = running_total
        else:
            last_total_entry = TotalModel.query.order_by(
                TotalModel.id.desc()
            ).first()
            last_grand_total = (
                last_total_entry.grand_total if last_total_entry else Decimal("0")
            )

            combined_total = daily_total + last_grand_total
            print(
                f"daily_total: {daily_total} + "
                f"last_grand_total: {last_grand_total} -----> "
                f"combined_total: {combined_total}"
            )

            total_annual_salary = db.session.query(
                db.func.sum(CostsPerProgramModel.salary)
            ).scalar() or Decimal("0")

            daily_salary_cost = total_annual_salary / 365
            print(
                f"total_annual_salary: {total_annual_salary} / 365 "
                f"-----> daily_salary_cost: {daily_salary_cost}"
            )

            final_total = combined_total - daily_salary_cost
            print(
                f"combined_total: {combined_total} - "
                f"daily_salary_cost: {daily_salary_cost} -----> "
                f"final_total: {final_total}"
            )

            new_total = TotalModel(
                grand_total=final_total,
                comment="program numbers entry",
                entry_date=datetime.now(),
            )
            db.session.add(new_total)

        db.session.commit()
        return redirect(url_for("main.index"))


    programs = ProgramModel.query.all()
    last_entries = {
        program.id: (
            DailyEntriesModel.query.filter_by(program_id=program.id)
            .order_by(DailyEntriesModel.date.desc())
            .first()
        ).number_of_participants
        if DailyEntriesModel.query.filter_by(program_id=program.id)
        .order_by(DailyEntriesModel.date.desc())
        .first()
        else 0
        for program in programs
    }

    return render_template(
        "add_daily_totals.html", programs=programs, last_entries=last_entries
    )


@main.route('/view_database')
def view_database():
    programs = ProgramModel.query.all()
    staff = CostsPerProgramModel.query.all()
    entries = DailyEntriesModel.query.all()
    return render_template('view_database.html', programs=programs, staff=staff, entries=entries)

@main.route('/add_one_time_cost', methods=['GET', 'POST'])
def add_one_time_cost():
    if request.method == 'POST':
        float_value = request.form.get("float_value", "").strip()
        float_value = Decimal(float_value)
        description = request.form['description']

        latest_total = TotalModel.query.order_by(TotalModel.id.desc()).first()

        if latest_total:
            from datetime import datetime
            updated_total = latest_total.grand_total - float_value

            new_total = TotalModel(
                grand_total=updated_total,
                comment=description,
                entry_date=datetime.now(),
                amount=float_value
            )
            db.session.add(new_total)
            db.session.commit()

            return redirect(url_for('main.index'))

        else:
            return "No existing total found in the database", 404

    return render_template('add_one_time_cost.html')

@main.route('/adjust_program_rates', methods=['GET', 'POST'])
def adjust_program_rates():
    all_programs = ProgramModel.query.order_by(ProgramModel.name).all()
    if request.method == 'POST':
        program_name = request.form['program_name']
        new_rate = float(request.form['new_rate'])

        program = ProgramModel.query.filter_by(name=program_name).first()

        program.rate = new_rate
        db.session.commit()
        message = f"Rate updated for {program_name}."

        return render_template('adjust_program_rates.html', message=message, programs=all_programs)

    return render_template('adjust_program_rates.html', programs=all_programs)
