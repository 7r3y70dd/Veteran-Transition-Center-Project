# from .models import User
from . import db
from flask import render_template, request, redirect, url_for, Blueprint
from .models import CostsPerProgramModel, ProgramModel, DailyEntriesModel

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/add_data')
def add_data():
    return render_template('add_data.html')

@main.route('/add_delete_support_staff', methods=['GET', 'POST'])
def add_delete_support_staff():
    if request.method == 'POST':
        # Get the data from the form
        program_name = request.form['program_name']
        employee_name = request.form['employee_name']
        salary = float(request.form['salary'])
        action = request.form['action']  # Action to determine if we're adding or deleting

        # Fetch the program from the database
        program = ProgramModel.query.filter_by(name=program_name).first()

        if program:
            if action == 'add':
                # Add the support staff to the database
                new_support_staff = CostsPerProgramModel(
                    program_id=program.id,
                    name=employee_name,
                    salary=salary
                )
                db.session.add(new_support_staff)
                db.session.commit()
                return redirect(url_for('main.index'))

            elif action == 'delete':
                # Delete the staff from the database
                staff_to_delete = CostsPerProgramModel.query.filter_by(
                    program_id=program.id,
                    name=employee_name,
                    salary=salary
                ).first()

                if staff_to_delete:
                    db.session.delete(staff_to_delete)
                    db.session.commit()

                return redirect(url_for('main.index'))

        else:
            return "Program not found", 404

    # Render the form for GET request
    return render_template('add_delete_support_staff.html')

@main.route('/veiw_data')
def view_data():
    return "This is route one."


@main.route('/add_delete_program', methods=['GET', 'POST'])
def add_delete_program():
    if request.method == 'POST':
        # Get the data from the form
        program_name = request.form['program_name']
        rate = float(request.form['rate'])
        action = request.form['action']  # Action to determine if we're adding or deleting

        if action == 'add':
            # Create a new ProgramModel entry
            new_program = ProgramModel(program_name=program_name, rate=rate)

            # Add the new entry to the database
            db.session.add(new_program)
            db.session.commit()
            return redirect(url_for('main.index'))  # Redirect to the index or another page

        elif action == 'delete':
            # Find the program to delete
            program_to_delete = ProgramModel.query.filter_by(name=program_name, rate=rate).first()

            if program_to_delete:
                # Delete the program from the database
                db.session.delete(program_to_delete)
                db.session.commit()

            return redirect(url_for('main.index'))  # Redirect after deletion

    # If the request method is GET, render the form
    return render_template('add_delete_program.html')
@main.route('/add_daily_totals', methods=['GET', 'POST'])
def add_daily_totals():
    if request.method == 'POST':
        # Get all the data from the form
        entries = request.form.getlist('number_of_participants')  # Get all participant numbers
        entry_date = request.form['date']

        for i, program in enumerate(ProgramModel.query.all()):
            number_of_participants = int(entries[i]) if entries[i] else 0
            program_name = program.name

            # Fetch the program from the database
            program = ProgramModel.query.filter_by(name=program_name).first()

            if program:
                # Check if a daily entry already exists for this program on the given date
                existing_entry = DailyEntriesModel.query.filter_by(
                    program_id=program.id,
                    date=entry_date
                ).first()

                if existing_entry:
                    # If entry exists, update the number of participants
                    existing_entry.number_of_participants = number_of_participants
                    db.session.commit()
                else:
                    # If entry doesn't exist, create a new entry
                    new_daily_entry = DailyEntriesModel(
                        number_of_participants=number_of_participants,
                        program_id=program.id,
                        date=entry_date
                    )
                    db.session.add(new_daily_entry)
                    db.session.commit()

            else:
                # If the program doesn't exist
                return "Program not found", 404

        # Redirect after adding or updating
        return redirect(url_for('main.index'))

    # If the request method is GET, render the form
    programs = ProgramModel.query.all()
    last_entries = {}

    # Get the last entry for each program (not strictly necessary anymore)
    for program in programs:
        last_entry = DailyEntriesModel.query.filter_by(program_id=program.id).order_by(DailyEntriesModel.date.desc()).first()
        last_entries[program.id] = last_entry.number_of_participants if last_entry else 0

    return render_template('add_daily_totals.html', programs=programs, last_entries=last_entries)
