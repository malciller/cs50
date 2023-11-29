from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)],
                           render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], 
                           render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], 
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class APIKeyForm(FlaskForm):
    api_key = StringField('API Key', validators=[DataRequired()])
    submit = SubmitField('Submit')
