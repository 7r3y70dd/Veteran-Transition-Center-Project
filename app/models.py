from sqlalchemy import func

from . import db

from datetime import datetime
from . import db  # Import the db instance from your app
from datetime import date


# Define a CustomModel with three integers and calculated field
# class PopulationsModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True)  # Primary key
#     programOneNumberOfParticipants = db.Column(db.Integer, nullable=False)  # First integer value
#     programTwoNumberOfParticipants = db.Column(db.Integer, nullable=False)  # Second integer value
#     programThreeNumberOfParticipants = db.Column(db.Integer, nullable=False)  # Third integer value
#     programOnePayPerDiem = db.Column(db.Integer, nullable=False)
#     programTwoPayPerDiem = db.Column(db.Integer, nullable=False)
#     programThreePayPerDiem = db.Column(db.Integer, nullable=False)
#     grandTotal = db.Column(db.Float, default=0)
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)  # Current date as timestamp
#
#
#     def __init__(self, value1, value2, value3):
#         # Initialize with the three values
#         self.programOneNumberOfParticipants = value1
#         self.programTwoNumberOfParticipants = value2
#         self.programThreeNumberOfParticipants = value3
#         # Automatically calculate the calculated_value from the three integers
#         rates = RatesModel.query.first()
#         self.programOnePayPerDiem = (self.programOneNumberOfParticipants * rates.rate_1)
#         self.programTwoPayPerDiem = (self.programTwoNumberOfParticipants * rates.rate_2)
#         self.programThreePayPerDiem = (self.programThreeNumberOfParticipants * rates.rate_3)
#         costs = CostsPerProgramModel.query.all()
#         self.grandTotal = self.programOnePayPerDiem + self.programTwoPayPerDiem + self.programThreePayPerDiem
#         value = self.grandTotal
#         for cost in costs:
#             value -= cost.salary / 365
#         self.grandTotal = value
#
#
#
#     # # Method to calculate the value (example: sum of the three integers)
#     # def calculate_value(self, program):
#     #     # Here, we simply sum the three values, but you can modify it to any formula.
#     #     if program == 1:
#     #         related_integer = RatesModel.query.first()
#     #         return self.value1 * related_integer.rate1
#     #     elif program == 1:
#     #         related_integer = RatesModel.query.first()
#     #         return self.value1 * related_integer.rate1
#
#     def __repr__(self):
#         return f"<CustomModel {self.id} | {self.value1}, {self.value2}, {self.value3}, {self.calculated_value}>"
#
# class RatesModel(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     # title = db.Column(db.String(100), nullable=False)
#     rate1 = db.Column(db.Integer, default=1)
#     rate2 = db.Column(db.Integer, default=1)
#     rate3 = db.Column(db.Integer, default=1)
#
#     def update_rates(self, rate_1=None, rate_2=None, rate_3=None):
#         if rate_1:
#             self.rate_1 = rate_1
#         if rate_2:
#             self.rate_2 = rate_2
#         if rate_3:
#             self.rate_3 = rate_3
#         self.last_updated = datetime.utcnow()
#         db.session.commit()

class CostsPerProgramModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program_model.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)

    def __init__(self, program_id, salary, name):
        self.program_id = program_id
        self.salary = salary
        self.name = name



class ProgramModel(db.Model):
    __tablename__ = 'program_model'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def __init__(self, program_name, rate):
        self.name = program_name
        self.rate = rate

class DailyEntriesModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_participants = db.Column(db.Integer, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program_model.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today())

    def __init__(self, number_of_participants, program_id, date):
        self.number_of_participants = number_of_participants
        self.program_id = program_id
        self.date = date


class TotalModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=date.today())
    grand_total = db.Column(db.Float, nullable=False)

    def __init__(self, grand_total, comment, entry_date=None):
        self.grand_total = grand_total
        self.comment = comment
        self.date = entry_date or date.today()

