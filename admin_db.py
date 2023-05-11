from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from shop import AdminLoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'C1B6-1F3C-4F1A-8F9C'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopdb.sqlite3'
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# Define the AdminLoginForm class


class AdminLoginForm(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Create a function to initialize the database


def init_database():
    # Create all tables
    db.create_all()

    # Add the initial admin login form to the database
    admin_login = AdminLoginForm(
        username='sepiaadmin', password='Roastery2023')
    db.session.add(admin_login)
    db.session.commit()


# Set up application context
with app.app_context():
    # Call the function to initialize the database
    init_database()
