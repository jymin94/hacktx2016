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
				welcome = { "Welcome" : {
							"count" : 1,
							"admin_response": "Welcome... friends."
						}
					}
				newpage = dict()
				newpage[pagename] = welcome
				print(newpage)
				# print(newkey)
				# newpage = { newkey : {
				# 		"Welcome" : {
				# 			"count" : 1,
				# 			"admin_response": "Welcome... friends."
				# 		}
				# 	}
				# }
				db.child("pages").child(str(pagename)).update(welcome);
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

@app.route("/page/<page_name>")
def page(page_name):
	child = None
	try :
		child = db.child("pages").child(page_name).get().val()
	except Exception as e: 
		print(e)
		return "you fucked up"
	# return str(OrderedDict(sorted(child.items(), key=lambda t: child[str(t)]['count'], reverse=True)))
	# print(str(sorted(child.items(), key=lambda t:child[str(t)]['count'], reverse=True)))
	print(str(OrderedDict(sorted(child.items(), key=lambda t: t[1]['count'], reverse=True))))
	# sorted_x = sorted(x.items(), key=child[])
	return "fuck"
#	return str(list(db.child("pages").child(page_name).child(str(key)).get().val() for(key) in sorted(child, key=lambda t: child[str(t)]['count'], reverse=True)))

# TODO authentication check before changing database

if __name__ == "__main__":
    app.run(debug=True)
