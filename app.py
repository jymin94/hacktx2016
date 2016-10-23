from firebase import firebase
from flask import *
import pyrebase
import requests
from collections import OrderedDict
from twilio.rest import TwilioRestClient 

ACCOUNT_SID = "AC4408e56e2ae7d6e2a53cca9ffac9865a" 
AUTH_TOKEN = "3f6dfdf42f5f1e2f7d7da02e642390f5" 

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 

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
	init_data = { "count" : 1, "admin_response" : admin_response, "resolved" : False }
	new_message[message] = init_data
	return new_message

def error_page(error_message):
	# 404 Error render_template for that
	return error_message

def validate_user():
	idToken = request.cookies.get('user_token')
	if idToken:
		try:
			user_uid = auth.get_account_info(idToken).get('users')[0].get('localId')
		except Exception as e:
			print(e)
			return False
		else:
			return user_uid in db.child("admin").shallow().get().val()
	return False

@app.route("/")
@app.route("/index")
def hello():
	login = "Invalid"
	if validate_user():
		login = "Valid"
	pagename = request.args.get('pagename')
	print(pagename)
	if pagename:
		return redirect("/pages/" + pagename)
	return render_template('index.html', login=login)

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
				db.child("pages").child(pagename).update(newpage);
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
		try:
			user =  auth.sign_in_with_email_and_password(email, password)
		except Exception as e:
			# TODO jonathon print('Wrong username/password. Please try again.')
			print(e)
			return render_template('login.html', login="Invalid")
		else:
			redirect_page = redirect('/')
			user_uid = user['localId']
			if user_uid in db.child("admin").shallow().get().val():
				pagename = db.child("admin").child(user_uid).get().val()
				redirect_page = redirect('/pages/' + pagename)
			response = make_response(redirect_page)
			response.set_cookie('user_token', user['idToken'])
			return response
		return redirect('/login')

@app.route("/logout")
def logout():
	resp = make_response(redirect("/"))
	try:
		resp.set_cookie('user_token', expires=0)
	except Exception as e:
		print(e)
		return error_page("Logout Unsuccessful: No logged in user found.") 
	return resp

@app.route("/pages/<page_name>/", methods=["GET", "POST"])
def page(page_name):
	if validate_user():
		print("user is properly logged in")
		return render_template('management.html')
	if request.method == 'POST':
		message = request.form['ticket_message']
		db.child('pages').child(page_name).update(init_message(message, "Not yet resolved"))
	return render_template('postpage.html')


@app.route("/pages/<page_name>/tickets")
def get_tickets(page_name):
	child = None
	try :
		child = db.child("pages").child(page_name).get().val()
	except Exception as e: 
		print(e)
		return error_page("No Page Named: " + page_name)
	return json.dumps({"data": sorted(child.items(), key=lambda t: t[1]['count'], reverse = True) })
	# In rememberance of our hard work below:
	# return json.dumps(OrderedDict(sorted(child.items(), key=lambda t: t[1]['count'], reverse=True)), sort_keys=False)

@app.route("/pages/<page_name>/tickets/<ticket_message>", methods=["GET", "DELETE"])
def upvote(page_name, ticket_message):
	if request.method == "GET":
		try:
			count = db.child("pages").child(page_name).child(ticket_message).child("count").get().val()
			if(count == 7 or count == 15 or count == 25):
				client.messages.create(
				    to="+17138358085", 
				    from_="+18327426436", 
				    body="URGENT TICKET: " + ticket_message 
				)
			db.child("pages").child(page_name).child(ticket_message).update({'count': count+1})
			return "ok"
		except Exception as e:
			print(e)
			return error_page("Error Updating: " + ticket_message)
	else:
		try:
			db.child("pages").child(page_name).child(ticket_message).remove()
			return "ok"	
		except Exception as e:
			print(e)
			return error_page("Error Removing Ticket: " + ticket_message)

@app.route("/pages/<page_name>/tickets/<ticket_message>/respond", methods=["GET", "POST"])
def admin_response(page_name, ticket_message):
	if request.method == 'POST':
		if validate_user():
			response = request.form["admin_response"]
			try:
				db.child("pages").child(page_name).child(ticket_message).update({'admin_response': response})
			except Exception as e:
				print(e)
				return error_page("Error Updating Ticket: " + ticket_message)
			# else:
				# return "ur not a valid admin this is bad real bad michael jackson"
		else:
			return "Error: invalid user"
	return "ok"

@app.route("/pages/<page_name>/resolved")
def get_resolved(page_name):
	child = db.child("pages").child(page_name).get().val()
	resolved_tickets = OrderedDict(filter(lambda x: x[1].get("resolved") == True, child.items()))
	return json.dumps({"data": sorted(resolved_tickets.items(), key=lambda t: t[1]['count'], reverse = True) })
	
@app.route("/pages/<page_name>/unresolved")
def get_unresolved(page_name):
	child = db.child("pages").child(page_name).get().val()
	unresolved_tickets = OrderedDict(filter(lambda x: x[1].get("resolved") == False, child.items()))
	return json.dumps({"data": sorted(unresolved_tickets.items(), key=lambda t: t[1]['count'], reverse = True) })

@app.route("/pages/<page_name>/tickets/<ticket_message>/resolve")
def resolve_ticket(page_name, ticket_message):
	if validate_user():
		try:
			db.child("pages").child(page_name).child(ticket_message).update({'resolved': True})
		except Exception as e:
			print(e)
			return error_page("Error Resolving Ticket: " + ticket_message)
		else:
			print("Successfully resolved ticket " + ticket_message)
			return "ok"
	else:
		return error_page("Pls log in")

@app.route("/pages/<page_name>/tickets/<ticket_message>/unresolve")
def unresolve_ticket(page_name, ticket_message):
	if validate_user():
		try:
			db.child("pages").child(page_name).child(ticket_message).update({'resolved': False})
		except Exception as e:
			print(e)
			return error_page("Error Unresolving Ticket: " + ticket_message)
		else:
			print("Successfully unresolved ticket " + ticket_message)
			return "ok"
	else:
		return error_page("Pls log in")

if __name__ == "__main__":
    app.run(debug=True)
