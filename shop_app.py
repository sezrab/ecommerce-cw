from datetime import datetime
import os
import time
from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, ValidationError, FileField, IntegerField
from wtforms.validators import Length, DataRequired, Email, Regexp, NumberRange
from flask_sqlalchemy import SQLAlchemy
from utils import create_pdf_from_2d_list

app = Flask(__name__)
app.config['SECRET_KEY'] = 'C1B6-1F3C-4F1A-8F9C'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopdb.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


class ExpiryDateValidator:
    def __call__(self, form, field):
        try:
            expiry_date = datetime.strptime(field.data, '%m/%y')
        except ValueError:
            raise ValidationError(
                'Invalid expiry date format. Please use MM/YY format.')
        current_date = datetime.now()


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()], render_kw={
                           "type": "password"})
    submit = SubmitField("Login")

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if not authenticate(self.username.data, self.password.data):
            self.password.errors.append('Invalid password')
            # reset password field
            self.password.data = ''
            return False

        return True


class CheckoutForm(FlaskForm):
    name = StringField('Name on Card', validators=[DataRequired(
        message="This can't be empty")], render_kw={"placeholder": "e.g. John Smith"})
    email = StringField('Email',
                        validators=[Email(message='Invalid email address'),
                                    DataRequired(
                                        message="This can't be empty")
                                    ],
                        render_kw={
                            "placeholder": "e.g. johnsmith@gmail.com"}
                        )
    card = StringField('Card Number',
                       validators=[
                           DataRequired(message="This can't be empty"),
                           Length(min=16, max=16,
                                  message='Card number must be 16 digits long'),
                           Regexp('^[0-9 -]*$', message='Card number must be numeric')],
                       render_kw={"placeholder": "e.g. 1122334455667788"}
                       )
    expiry = StringField('Expiry Date (MM/YY)', validators=[DataRequired(message="This can't be empty"), Regexp(
        r'^(0[1-9]|1[0-2])\/[0-9]{2}$', message='Invalid expiry date format. Please use MM/YY format.'),


    ],
        render_kw={"placeholder": "e.g. 12/22"})
    cvc = StringField('CVC', validators=[
        DataRequired(message="This can't be empty"),
        Regexp('^[0-9]*$', message='CVC must be numeric'),
        Length(min=3, max=3, message='CVC must be 3 digits long')
    ], render_kw={"placeholder": "e.g. 123"})
    submit = SubmitField('Submit')


class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    # file upload
    image = FileField('Image', validators=[DataRequired()])
    price = FloatField('Price', validators=[
                       DataRequired(), NumberRange(min=0)])
    airmiles = IntegerField('Airmiles', validators=[
        DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


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
    airmiles = db.Column(db.Integer, nullable=False)

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


def sort(method, products):
    # Sort the products based on the selected option
    if method == 'price_low_high':
        sorted_products = sorted(products, key=lambda p: p.price)
    elif method == 'price_high_low':
        sorted_products = sorted(
            products, key=lambda p: p.price, reverse=True)
    elif method == 'airmiles_low_high':
        sorted_products = sorted(products, key=lambda p: p.airmiles)
    else:
        sorted_products = sorted(products, key=lambda p: p.name)
    return sorted_products


@ app.route('/', methods=['GET', 'POST'])
def index():
    # Retrieve the selected sorting option
    selected_option = request.form.get('sort')
    items_sorted = sort(selected_option, Item.query.all())
    return render_template('index.html', items=items_sorted, selected_option=selected_option, basket_count=len(session.get('basket', [])))


def authenticate(username, password):
    admin = Admin.query.filter_by(username=username).first()
    if not admin:
        return False
    return admin.password == password


def delete_item(item):
    db.session.delete(item)
    db.session.commit()


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AdminLoginForm()
    if form.validate_on_submit():
        session['username'] = form.username.data
        session['password'] = form.password.data
        # check if username and password match any in database admin table
        if authenticate(form.username.data, form.password.data):
            return redirect(url_for('admin_dashboard'))
        else:
            print('Incorrect username or password')
    return render_template('admin.html', form=form)


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    try:
        username = session['username']
        password = session['password']
    except KeyError:
        return redirect(url_for('admin'))
    if not authenticate(username, password):
        return redirect(url_for('admin'))
    form = ItemForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = str(time.time())+"_"+image.filename
        # save to static\images
        image.save(os.path.join('static/images', filename))
        item = Item(name=form.name.data, description=form.description.data,
                    image=filename, price=form.price.data, airmiles=form.airmiles.data)
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_dashboard.html', form=form)


@ app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    items, total = getItemsFromBasket(session.get('basket', []))
    form = CheckoutForm()
    if form.validate_on_submit():
        # clear basket
        session['receipt_basket'] = session['basket']
        session['basket'] = []
        return success()
    return render_template('checkout.html', form=form, items=items, total=total)


@app.route('/receipt', methods=['GET', 'POST'])
def receipt():
    items, total = getItemsFromBasket(session.get('receipt_basket', []))
    table = [['Item', 'Quantity', 'Price (£)']]
    for item in items:
        table.append([item.name, items[item], '%.2f' %
                     (item.price * items[item])])
    table.append(['Total', '', '%.2f' % total])
    rcpt_path = 'receipts/receipt-%i.pdf' % int(time.time())
    create_pdf_from_2d_list(
        table, rcpt_path)
    return send_file(rcpt_path, as_attachment=True)


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


@ app.route('/delete', methods=['POST'])
def delete():
    if authenticate(session.get('username', ''), session.get('password', '')):
        try:
            itmid = request.form.get('id')
            # get item with id
            item = Item.query.get(itmid)
            delete_item(item)
        except:
            pass
    return redirect(url_for('index'))


@ app.route('/view', methods=['GET'])
def view():
    itemid = request.args.get('id')
    return render_template('product.html', item=Item.query.get(itemid), basket_count=len(session.get('basket', [])), admin=authenticate(session.get('username', ''), session.get('password', '')))


if __name__ == '__main__':
    app.run(debug=True)
