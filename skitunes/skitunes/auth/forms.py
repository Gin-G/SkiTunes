from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from skitunes.account.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Name', 
        validators=[DataRequired(message="Name is required"), 
                    Length(min=2, max=50, message="Name must be between 2 and 50 characters")])
    email = StringField('Email', 
        validators=[DataRequired(message="Email is required"), 
                    Email(message="Invalid email format")])
    password = PasswordField('Password', 
        validators=[
            DataRequired(message="Password is required"), 
            Length(min=8, max=100, message="Password must be at least 8 characters long")
        ])
    confirm_password = PasswordField('Confirm Password', 
        validators=[
            DataRequired(message="Confirmation password is required"), 
            EqualTo('password', message='Passwords must match')
        ])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        """Custom validation to check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[
            DataRequired(message="Email is required"), 
            Email(message="Invalid email format")
        ])
    password = PasswordField('Password', 
        validators=[DataRequired(message="Password is required")])
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