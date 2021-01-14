from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,EqualTo,Length,Email,NumberRange
class RegistrationForm(FlaskForm):
    companyname=StringField('Companyname')
    username=StringField('Username',validators=[DataRequired(message='Enter Valid Name'),Length(min=2,max=20,message="Enter Name Range Between 2 and 20")])
    password=PasswordField('Password',validators=[DataRequired(message='Enter Valid Email')])
    email=StringField('Email',validators=[Email(message='Enter Valid Mail Address')])
    phone=StringField('Phone',validators=[DataRequired(message='Enter valid Phone Number'),Length(min=10,max=10,message='Enter Valid Phone Number')])
    confirmpassword=PasswordField('Confirm Password',validators=[DataRequired(message='Enter Valid Password'),EqualTo('password')])
    submit=SubmitField('Sign Up',validators=[DataRequired()])
class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login',validators=[DataRequired()])