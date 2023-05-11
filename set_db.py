from sqlalchemy.exc import OperationalError
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from shop_app import AdminLoginForm, Item

app = Flask(__name__)
app.config['SECRET_KEY'] = 'C1B6-1F3C-4F1A-8F9C'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopdb.sqlite3'
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


items = [
    Item(
        name='Sepia "Icon" Espresso Blend',
        description='A blend of 3 different coffees from 3 different continents. The result is a complex, full-bodied espresso with a rich crema and a sweet, lingering finish. The Icon is a blend of 50% Brazil, 25% Guatemala and 25% Ethiopia. It\'s travelled further than you ever will and boy can you taste it.',
        image='espresso.jpg',
        price=18.30,
        airmiles=49723
    ),

    Item(
        name='Cold Brew Classic',
        description='Let your friends know that you think you\'re better than them with this cold brew. It\'s a classic, and way as well be river water in a jam jar. But it\'s cold, and it\'s brewed, and you\'re buying it. So it\'s cold brew.',
        image='cold.jpg',
        price=12.29,
        airmiles=4210,
    ),

    Item(
        name='Ground Filter Coffee',
        description='We swept up beans from the factory floor, and we ground them. Then we put them in a bag. Then we put that bag in a box. Then we put that box in a bigger box and wrapped it in plastic. Enjoy.',
        image='filter.jpg',
        price=9.99,
        airmiles=2710,
    ),

    Item(
        name='French Blend',
        description='Grown in india, roasted in Germany, we don\'t know how this has anything to do with France. But it sells well, and it\'s cheap to import. So we\'re not complaining.',
        image='french.jpg',
        price=8.99,
        airmiles=2049,
    ),

    Item(
        name='Iced Coffee',
        description='Pond water + lots of sugar + ice = iced coffee. The young\'uns love it.',
        image='iced.jpg',
        price=15.99,
        airmiles=2018,
    ),

    Item(
        name='Sunday Morning Latte',
        description='Take our specialised latte blend with a shot of caramel. It\'s a Sunday morning, and you\'re hungover. You\'re not going manage any work today. You\'re going to drink this latte, and you\'re going to watch Netflix. And you\'re going to enjoy it.',
        image='latte.jpg',
        price=15.99,
        airmiles=1023,
    ),

    Item(
        name='Mocha',
        description='Literally the same product as our Latte, but we hiked the price up because you\'re going to put hot chocolate in it. You\'re a sucker for marketing, idiot.',
        image='mocha.jpg',
        price=15.99,
        airmiles=1120,
    ),
]


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
    for item in items:
        db.session.add(item)

    db.session.commit()


# Set up application context
with app.app_context():
    try:
        # Call the function to initialize the database
        init_database()
        print("Database initialization completed successfully.")
    except OperationalError as e:
        print("OperationalError:", e)
