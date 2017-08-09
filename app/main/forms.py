from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    photo = FileField('Photo image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    body = PageDownField("Hi, share us something!", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = StringField('Any comment?', validators=[Required()])
    submit = SubmitField('Submit')


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


class AddSensorForm(FlaskForm):
    name = StringField('Sensor name', validators=[Length(0, 64)])
    about_sensor = TextAreaField('About sensor')
    submit = SubmitField('Add sensor')


class DeleteSensorForm(FlaskForm):
    sensor = SelectField('Sensors', coerce=int)
    submit = SubmitField('Delete sensor')

    def __init__(self, sensors, *args, **kwargs):
        super(DeleteSensorForm, self).__init__(*args, **kwargs)
        self.sensor.choices = [(sensor.id, sensor.name) for sensor in sensors]
        self.sensors = sensors
