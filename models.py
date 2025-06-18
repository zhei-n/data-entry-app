from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length

db = SQLAlchemy()


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)


class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    brand = StringField('Item Brand', validators=[DataRequired(), Length(max=100)])
    model = StringField('Item Model', validators=[DataRequired(), Length(max=100)])
    location = StringField('Item Location', validators=[DataRequired(), Length(max=100)])
    serial_number = StringField('Item Serial Number', validators=[DataRequired(), Length(max=100)])
    owner = StringField('Item Owner', validators=[DataRequired(), Length(max=100)])
    status = SelectField('Item Status', choices=[('Working', 'Working'), ('Defective', 'Defective'), ('Under Maintenance', 'Under Maintenance')], validators=[DataRequired()])
