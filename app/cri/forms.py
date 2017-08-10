from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Required, Length
from wtforms import ValidationError
from ..models import User, User_files


class EditSensorForm(FlaskForm):
    sensor = SelectField('Sensors', coerce=int)
    add = SubmitField('Add sensor')
    delete = SubmitField('Delete sensor')

    def __init__(self, sensors, *args, **kwargs):
        super(EditSensorForm, self).__init__(*args, **kwargs)
        self.sensor.choices = [(sensor.id, sensor.name) for sensor in sensors]
        self.sensors = sensors


class NoSensorForm(FlaskForm):
    add = SubmitField('Add sensor')


class SelectSensorForm(FlaskForm):
    sensor = SelectField('Sensors', coerce=int)
    submit = SubmitField('Plot Data')

    def __init__(self, sensors, *args, **kwargs):
        super(SelectSensorForm, self).__init__(*args, **kwargs)
        self.sensor.choices = [(sensor.id, sensor.name) for sensor in sensors]
        self.sensors = sensors
