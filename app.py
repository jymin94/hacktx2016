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
	init_data = { "count" : 1, "admin_response" : admin_response }
	new_message[message] = init_data
	return new_message

def error_page():
	# 404 Error render_template for that
	return "404 Error"

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
		resp = redirect('/')
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
			resp.set_cookie('user_token', user['idToken'])
		return resp
	return "ok"

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		email = request.form['email']
		password = request.form['password']
		user =  auth.sign_in_with_email_and_password(email, password)
		response = make_response(redirect('/'))
		response.set_cookie('user_token', user['idToken'])
		return response

# TODO logout
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
		return error_page()
	return json.dumps({"data": sorted(child.items(), key=lambda t: t[1]['count'], reverse = True) })
	# In rememberance of our hard work below:
	# return json.dumps(OrderedDict(sorted(child.items(), key=lambda t: t[1]['count'], reverse=True)), sort_keys=False)

@app.route("/pages/<page_name>/tickets/<ticket_message>", methods=["GET", "DELETE"])
def upvote(page_name, ticket_message):
	if request.method == "GET":
		try:
			count = db.child("pages").child(page_name).child(ticket_message).child("count").get().val()
			db.child("pages").child(page_name).child(ticket_message).update({'count': count+1})
			return "ok"
		except Exception as e:
			print(e)
			return error_page()
	else:
		try:
			db.child("pages").child(page_name).child(ticket_message).remove()
			return "ok"	
		except Exception as e:
			print(e)
			return error_page()

@app.route("/pages/<page_name>/tickets/<ticket_message>/respond", methods=["GET", "POST"])
def admin_response(page_name, ticket_message):
	if request.method == 'POST':
		idToken = request.cookies.get('user_token')
		if idToken:
			user_uid = auth.get_account_info(idToken).get('users')[0].get('localId')
			if user_uid in db.child("admin").shallow().get().val():
				response = request.form["admin_response"]
				try:
					db.child("pages").child(page_name).child(ticket_message).update({'admin_response': response})
				except Exception as e:
					print(e)
					return error_page()
			else:
				return "ur not a valid admin this is bad real bad michael jackson"
		else:
			return "pls log in"
	return "ok"

# TODO authentication check before changing database

if __name__ == "__main__":
    app.run(debug=True)
