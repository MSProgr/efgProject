import secrets
import os
from PIL import Image
from flask import render_template,url_for,flash,redirect, request
from flask_login import login_user,current_user,logout_user,login_required
from efg import app,db,bcrypt
from efg.forms import RegistrationForm, LoginForm, UpdateAccountForm, DossierForm
from efg.models import User, Dossier


@app.route('/')
def index():
	return render_template("index.html")

@app.route('/login',methods=["GET","POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for("account"))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user,remember=form.remember.data)
			next_page =  request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for("account"))
		else:
			flash("Veuillez vérifier l'email saisie ou le mot de pass","danger")
	return render_template('login.html',title="login",form=form)


@app.route('/register',methods=["GET","POST"])
@login_required
def register():
	if current_user.profile != "admin":
		flash("Opération non authorisée","danger")
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data,email=form.email.data,password=pwd,profile=form.profile.data)
		db.session.add(user)
		db.session.commit()
		flash('Compte crée avec succée.', 'success')
		return redirect(url_for('index'))
	return render_template('register.html',title="register",form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for("index"))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path,"static/profile_pics",picture_fn)
	#resizing the image
	output_size = (125,125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	#saving the picture
	i.save(picture_path)
	return picture_fn

@app.route("/account",methods=["GET","POST"])
@login_required
def account():
	image_file = url_for('static', filename="profile_pics/"+current_user.image_file)
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash("Mise à jour de votre compte réussit","danger")
		return redirect(url_for("account"))
	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template("account.html",image_file=image_file, form=form, title="account")


def save_fichier(form_fichier):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_fichier.filename)
	fichier_fn = random_hex + f_ext
	fichier_path = os.path.join(app.root_path,"static/fichiers",fichier_fn)
	form_fichier.save(fichier_path)
	return fichier_fn
 
@app.route("/dossier/new",methods=["GET","POST"])
@login_required
def dossier():
	dossiers = Dossier.query.all()
	if current_user.profile != "admin":
		return render_template("dossier_bank.html",dossiers="dossiers")
	else:
		form = DossierForm()
		if form.validate_on_submit():
			dossier = Dossier(description=form.description.data,user_id=current_user.id)
			fichier_file = save_fichier()
			dossier.fichier = fichier_file
			dossier.user_id = current_user.id
			db.session.save(dossier)
			db.session.commit()
			return redirect(url_for("dossier"))
		return render_template("dossier.html",form=form,title="nouveau fichier",dossiers=dossiers)