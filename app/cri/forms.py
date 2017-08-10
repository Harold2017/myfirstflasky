from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Required, Length
from wtforms import ValidationError
from ..models import User, User_files


class EditSpectrumForm(FlaskForm):
    spectrum = SelectField('Spectrum', coerce=int)
    add = SubmitField('Add spectrum')
    delete = SubmitField('Delete spectrum')

    def __init__(self, spectrum, *args, **kwargs):
        super(EditSpectrumForm, self).__init__(*args, **kwargs)
        self.s.choices = [(s.id, s.name) for s in spectrum]
        self.spectrum = spectrum


class NoSpectrumForm(FlaskForm):
    add = SubmitField('Add spectrum')


class SelectSpectrumForm(FlaskForm):
    spectrum = SelectField('Spectrum', coerce=int)
    submit = SubmitField('Show spectrum')

    def __init__(self, spectrum, *args, **kwargs):
        super(SelectSpectrumForm, self).__init__(*args, **kwargs)
        self.s.choices = [(s.id, s.name) for s in spectrum]
        self.spectrum = spectrum
