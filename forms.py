from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


from wtforms import SelectField
from wtforms.validators import Length


class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    brand = StringField('Item Brand', validators=[DataRequired(), Length(max=100)])
    model = StringField('Item Model', validators=[DataRequired(), Length(max=100)])
    location = StringField('Item Location', validators=[DataRequired(), Length(max=100)])
    serial_number = StringField('Item Serial Number', validators=[DataRequired(), Length(max=100)])
    owner = StringField('Item Owner', validators=[DataRequired(), Length(max=100)])
    status = SelectField('Item Status', choices=[('Working', 'Working'), ('Defective', 'Defective'), ('Under Maintenance', 'Under Maintenance')], validators=[DataRequired()])
