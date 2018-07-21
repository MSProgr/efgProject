from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from efg.models import User, Dossier
from flask_login import current_user

class RegistrationForm(FlaskForm):
	username = StringField("Username",validators=[DataRequired(),Length(min=2,max=50)])
	email = StringField("Email",validators=[DataRequired(),Email()])
	password = PasswordField("Password",validators=[DataRequired(),Length(min=5)])
	confirm_password = PasswordField("Confirm Password",validators=[EqualTo("password")])
	profile = SelectField("Profile",choices=[('admin',"Administrateur"),('bank',"Banque")])
	submit = SubmitField("Sign Up")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("Nom d'utilisateur déja pris.Veuillez choisir un autre")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("Email déja pris. Veuillez choisir un autre")

class LoginForm(FlaskForm):
	email = StringField("Email",validators=[DataRequired(),Email()])
	password = PasswordField("Password",validators=[DataRequired(),Length(min=5)])
	remember = BooleanField("Remember Me")
	submit = SubmitField("Sign In")

class UpdateAccountForm(FlaskForm):
	username = StringField("Username",validators=[DataRequired(),Length(min=2,max=50)])
	email = StringField("Email",validators=[DataRequired(),Email()])
	picture = FileField("photo de profile", validators=[FileAllowed(["pjg","png","jpeg"])])
	submit = SubmitField("Modifer")

	def validate_username(self, username):
		if current_user.username != username.data:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError("Nom d'utilisateur déja pris.Veuillez choisir un autre")

	def validate_email(self, email):
		if current_user.email != email.data:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError("Email déja pris. Veuillez choisir un autre")

class DossierForm(FlaskForm):
	description = TextAreaField("Description",validators=[DataRequired(),Length(min=2)])
	fichier = FileField("Fichier",validators=[FileRequired(),FileAllowed(["pdf"])])
	submit = SubmitField("Envoyer")