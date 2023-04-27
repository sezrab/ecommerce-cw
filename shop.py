from flask import Flask, render_template, request
# flask bootstrap
from flask_bootstrap import Bootstrap
# flaskwtf form
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired


# get sql alchemy from flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopdb.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', items=Item.query.all())


@app.route('/view', methods=['GET'])
def view():
    itemid = request.args.get('id')
    return render_template('product.html', item=Item.query.get(itemid))


if __name__ == '__main__':
    app.run(debug=True)
