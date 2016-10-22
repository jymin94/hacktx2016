from firebase import firebase
from flask import *
import pyrebase
import requests

config = {
	"apiKey" : 'AIzaSyAFAM421tHTh5AWZzXvp8WBTF3TeJIaWe4',
	"authDomain" : "my-awesome-project-13077.firebaseapp.com",
	"databaseURL" : "https://my-awesome-project-13077.firebaseio.com/",
	"storageBucket" : "my-awesome-project-13077.appspot.com"
}


app = Flask(__name__)
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

@app.route("/")
@app.route("/index")
def hello():
	return render_template('index.html')

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
	if request.method == 'GET':
		return render_template('signup.html')
	else:
		email = request.form["email"]
		password = request.form["password"]
		try:
			auth.create_user_with_email_and_password(email, password)
		except requests.exceptions.HTTPError as e:
			print(e)
			# TODO process based on error
			return "fucku"
		return redirect('/')
	return "ok" 

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'GET':
		email = request.args.get('email')
		print("HELLO" + email)
		password = request.args.get('password')
		print("BYE " + password)
		user =  auth.sign_in_with_email_and_password(email, password)
		return user

# TODO authentication check before changing database

if __name__ == "__main__":
    app.run(debug=True)
