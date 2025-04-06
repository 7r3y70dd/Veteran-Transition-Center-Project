# from .models import User
from . import db
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/add_data')
def add_data():
    return "This is route one."

@main.route('/veiw_data')
def view_data():
    return "This is route one."

