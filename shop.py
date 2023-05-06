from flask import Flask, redirect, render_template, request, session, url_for
# flask bootstrap
from flask_bootstrap import Bootstrap
# flaskwtf form
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import Length, DataRequired, Email, Regexp
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = ['C1B6-1F3C-4F1A-8F9C']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopdb.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


class CheckoutForm(Form):
    # 4)	Another page (checkout) should allow the user to enter their credit card payment details, and confirm the final price to be paid.
    # a)	As the user steps through the fields of the form, help messages must appear explaining what information needs to be entered in each field.
    # 5)	Do not implement an actual checkout or secure payment mechanism. Instead, implement a basic validation for the payment form to check that, when the form is submitted,
    # a)	the entered credit card number is a 16 digit number (you may permit dashes and spaces),
    # b)	that none of the other required fields are empty,
    # c)	plus any other validation checks you think necessary.
    # If the submitted form validates correctly, present a page saying that checkout was successful. If there are errors in the form (e.g. the credit card number field contains other text) you may either prevent the form from submitting, or report an error after it submits.

    name = StringField('Name on Card', validators=[DataRequired(
        message="This can't be empty")])
    email = StringField('Email',
                        validators=[
                            DataRequired(message="This can't be empty"),
                            Email(message='Invalid email address')]
                        )
    card = StringField('Card Number',
                       validators=[
                           DataRequired(message="This can't be empty"),
                           Length(min=16, max=16,
                                  message='Card number must be 16 digits long'),
                           Regexp('^[0-9 -]*$', message='Card number must be numeric')]
                       )
    expiry = DateField('Expiry Date', format='%m/%y',
                       validators=[DataRequired(message="This can't be empty")])
    cvc = IntegerField('CVC', validators=[
                       DataRequired(message="This can't be empty")])
    submit = SubmitField('Submit')


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    # •	Name
    # •	Textual description
    # •	Picture
    # •	Price
    # •	Measure of environmental impact e.g. carbon or ecological footprint
    name = db.Column(db.String(32), index=True, unique=True, nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    image = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    airmiles = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Item {0}>'.format(self.name)


def getItemsFromBasket(basket):
    # items = Item.query.filter(Item.id.in_(item_ids)).all()
    items = {}
    for id in basket:
        itm = Item.query.get(id)
        if itm not in items:
            items[itm] = 1
        else:
            items[itm] = items[itm] + 1
    total = 0
    for item in items:
        count = items[item]
        total += item.price * count
    return items, total


@ app.route('/', methods=['GET'])
def index():
    return render_template('index.html', items=Item.query.all(), basket_count=len(session.get('basket', [])))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    items, total = getItemsFromBasket(session.get('basket', []))
    return render_template('checkout.html', form=CheckoutForm(), items=items, total=total)


@ app.route('/basket', methods=['GET'])
def basket():
    items, total = getItemsFromBasket(session.get('basket', []))
    return render_template('basket.html', items=items, basket_count=len(session.get('basket', [])), total=total)


@ app.route('/add', methods=['POST'])
def add():
    # add to basket
    if 'basket' not in session:
        session['basket'] = []
    itmid = request.form.get('id')
    print(itmid)
    session['basket'] = session['basket'] + [itmid]
    print(session['basket'])
    return redirect(url_for('index'))


@ app.route('/remove', methods=['POST'])
def remove():
    # remove from basket
    if 'basket' not in session:
        session['basket'] = []
    itmid = request.form.get('id')

    # REMOVE FIRST OCCURENCE ONLY OF ITMID FROM BASKET
    basket = session['basket']
    idx = basket.index(itmid)
    basket.pop(idx)
    session['basket'] = basket
    return redirect(url_for('basket'))


@ app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', basket_count=len(session.get('basket', [])))


@ app.route('/view', methods=['GET'])
def view():
    itemid = request.args.get('id')
    return render_template('product.html', item=Item.query.get(itemid), basket_count=len(session.get('basket', [])))


if __name__ == '__main__':
    app.run(debug=True)
