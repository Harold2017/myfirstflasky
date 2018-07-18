from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import Required


class LabForm(FlaskForm):
    L = FloatField('L', validators=[Required()])
    a = FloatField('a', validators=[Required()])
    b = FloatField('b', validators=[Required()])
    submit = SubmitField('Plot')
