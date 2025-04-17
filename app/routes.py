# from .models import User
from datetime import timedelta

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
                    salary=salary,
                    name=employee_name
                )
                db.session.add(new_support_staff)
                db.session.commit()
                return redirect(url_for('main.index'))

            elif action == 'delete':
                # Delete the staff from the database
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

    # Render the form for GET request
    return render_template('add_delete_support_staff.html')

@main.route('/veiw_data')
def view_data():
    return render_template('view_data.html')


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
        from datetime import datetime


        entries = request.form.getlist('number_of_participants')
        entry_date = datetime.now()  # Use current datetime directly

        # entries = request.form.getlist('number_of_participants')
        # entry_date_str = request.form['date']
        # entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d')

        daily_total = 0.0

        for i, program in enumerate(ProgramModel.query.all()):
            number_of_participants = int(entries[i]) if entries[i] else 0
            program_rate = program.rate

            # Calculate this program's contribution to the daily total
            daily_total += float(number_of_participants) * program_rate

            print(f"Checking for existing entry - Program ID: {program.id}, Date: {entry_date}")

            # Check if a daily entry already exists
            existing_entry = DailyEntriesModel.query.filter_by(
                program_id=program.id,
                date=entry_date.date()
            ).first()

            if existing_entry:
                existing_entry.number_of_participants = number_of_participants
            else:
                print(f"No existing entry found for Program ID {program.id} on {entry_date}, will create a new one.")
                new_entry = DailyEntriesModel(
                    number_of_participants=number_of_participants,
                    program_id=program.id,
                    date=entry_date
                )
                db.session.add(new_entry)


        # After processing all programs, save the total
        # existing_total = TotalModel.query.filter_by(
        #     date=entry_date.date(),
        #     # comment='program numbers entry'
        # ).first()
        existing_total = TotalModel.query.filter(
            func.date(TotalModel.date) == entry_date.date(),
            TotalModel.comment == 'program numbers entry'
        ).order_by(TotalModel.date.desc()).first()

        cutoff_date = entry_date.date() - timedelta(days=1)

        prior_entry = TotalModel.query.filter(
            TotalModel.date <= cutoff_date
        ).order_by(TotalModel.date.desc()).first()

        previous_grand_total = prior_entry.grand_total if prior_entry else float(0.0)

        updated_grand_total = previous_grand_total + daily_total

        if existing_total:
            existing_total.grand_total = updated_grand_total

            subsequent_entries = TotalModel.query.filter(
                TotalModel.date > existing_total.date,
                TotalModel.comment != 'program numbers entry'
            ).order_by(TotalModel.date.asc()).all()

            running_total = existing_total.grand_total

            print('starting total edited: ' + str(running_total))

            for entry in subsequent_entries:
                print('start runn  ' + str(running_total))
                print('entry:  ' + str(entry.grand_total))
                running_total = running_total - entry.amount
                entry.grand_total = running_total
        else:
            # Get the most recent total from the TotalModel table (if any)
            last_total_entry = TotalModel.query.order_by(TotalModel.id.desc()).first()
            last_grand_total = last_total_entry.grand_total if last_total_entry else 0.0

            # Add the current daily total to the last grand total
            combined_total = daily_total + last_grand_total

            total_annual_salary = db.session.query(
                db.func.sum(CostsPerProgramModel.salary)
            ).scalar() or 0.0
            daily_salary_cost = total_annual_salary / 365

            final_total = combined_total - daily_salary_cost

            # Create the new entry
            new_total = TotalModel(
                grand_total=final_total,
                comment='program numbers entry',
                entry_date=datetime.now()
            )
            db.session.add(new_total)

        db.session.commit()
        return redirect(url_for('main.index'))

    # If the request method is GET, render the form
    programs = ProgramModel.query.all()
    last_entries = {}

    # Get the last entry for each program (not strictly necessary anymore)
    for program in programs:
        last_entry = DailyEntriesModel.query.filter_by(program_id=program.id).order_by(DailyEntriesModel.date.desc()).first()
        last_entries[program.id] = last_entry.number_of_participants if last_entry else 0

    return render_template('add_daily_totals.html', programs=programs, last_entries=last_entries)


@main.route('/view_database')
def view_database():
    programs = ProgramModel.query.all()
    staff = CostsPerProgramModel.query.all()
    entries = DailyEntriesModel.query.all()
    return render_template('view_database.html', programs=programs, staff=staff, entries=entries)

@main.route('/add_one_time_cost', methods=['GET', 'POST'])
def add_one_time_cost():
    if request.method == 'POST':
        # Get the float value (one-time cost) and the description from the form
        float_value = float(request.form['float_value'])
        description = request.form['description']

        # Get the latest total value from the TotalModel table
        latest_total = TotalModel.query.order_by(TotalModel.id.desc()).first()

        if latest_total:
            from datetime import datetime
            # Subtract the one-time cost from the latest total
            updated_total = latest_total.grand_total - float_value

            # Create a new row in the TotalModel table with the updated total
            new_total = TotalModel(
                grand_total=updated_total,
                comment=description,
                entry_date=datetime.now(),
                amount=float_value
            )
            db.session.add(new_total)
            db.session.commit()

            # Redirect after adding the new entry
            return redirect(url_for('main.index'))

        else:
            # If there's no total record yet, return an error (or handle as needed)
            return "No existing total found in the database", 404

    # If GET request, just render the form
    return render_template('add_one_time_cost.html')

@main.route('/adjust_program_rates', methods=['GET', 'POST'])
def adjust_program_rates():
    if request.method == 'POST':
        program_name = request.form['program_name']
        new_rate = float(request.form['new_rate'])

        # Look up the program by name
        program = ProgramModel.query.filter_by(name=program_name).first()

        if program:
            program.rate = new_rate
            db.session.commit()
            message = f"Rate updated for {program_name}."
        else:
            message = f"Program '{program_name}' not found."

        return render_template('adjust_program_rates.html', message=message)

    return render_template('adjust_program_rates.html')
