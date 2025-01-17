from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from skitunes.account.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Name', 
        validators=[DataRequired(message="Name is required"), 
                    Length(min=2, max=50, message="Name must be between 2 and 50 characters")],
        render_kw={"placeholder": "Name"})
    email = StringField('Email', 
        validators=[DataRequired(message="Email is required"), 
                    Email(message="Invalid email format")],
        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', 
        validators=[
            DataRequired(message="Password is required"), 
            Length(min=8, max=100, message="Password must be at least 8 characters long")
        ],
        render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', 
        validators=[
            DataRequired(message="Confirmation password is required"), 
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[
            DataRequired(message="Email is required"), 
            Email(message="Invalid email format")
        ],
        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', 
        validators=[DataRequired(message="Password is required")],
        render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', 
        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', 
        validators=[DataRequired(), Length(min=8, max=100)])
    confirm_password = PasswordField('Confirm New Password', 
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Reset Password')