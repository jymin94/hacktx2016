from firebase import firebase
from flask import *
import pyrebase
import requests
from collections import OrderedDict

config = {
	"apiKey" : 'AIzaSyAFAM421tHTh5AWZzXvp8WBTF3TeJIaWe4',
	"authDomain" : "my-awesome-project-13077.firebaseapp.com",
	"databaseURL" : "https://my-awesome-project-13077.firebaseio.com/",
	"storageBucket" : "my-awesome-project-13077.appspot.com"
}

app = Flask(__name__)
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

def init_message(message, admin_response):
	new_message = dict()
	init_data = { "count" : 0, "admin_response" : admin_response }
	new_message[message] = init_data
	return new_message

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
		pagename = request.form["pagename"]
		try:
			auth.create_user_with_email_and_password(email, password)
		except requests.exceptions.HTTPError as e:
			print(e)
			# TODO process based on error
			return "There was an error creating a user."
		else:
			user =  auth.sign_in_with_email_and_password(email, password)
			if pagename not in db.child("pages").shallow().get().val():
				newpage = init_message("Welcome", "Welcome... friends.")
				print(newpage)
				db.child("pages").child(str(pagename)).update(newpage);
			newadmin = dict()
			newadmin[user["localId"]] = pagename
			db.child("admin").update(newadmin)

		return redirect('/')
	return "ok" 

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		email = request.form['email']
		password = request.form['password']
		user =  auth.sign_in_with_email_and_password(email, password)
		return redirect('/')

@app.route("/pages/<page_name>/", methods=["GET", "POST"])
def page(page_name):
	if request.method == 'POST':
		message = request.form['ticket_message']
		print(str(init_message(message, None)))
		db.child('pages').child(page_name).update(init_message(message, None))
	return render_template('postpage.html')


@app.route("/pages/<page_name>/tickets")
def get_tickets(page_name):
	child = None
	try :
		child = db.child("pages").child(page_name).get().val()
	except Exception as e: 
		print(e)
		return error_page
	return json.dumps(OrderedDict(sorted(child.items(), key=lambda t: t[1]['count'], reverse=True)))

@app.route("/pages/<page_name>/tickets/<ticket_message>")
def upvote(page_name, ticket_message):
	try:
		count = db.child("pages").child(page_name).child(ticket_message).child("count").get().val()
		db.child("pages").child(page_name).child(ticket_message).update({'count': count+1})
	except Exception as e:
		print(e)
		return error_page()

def error_page():
	# 404 Error render_template for that
	return "404 Error"

# TODO authentication check before changing database

if __name__ == "__main__":
    app.run(debug=True)
