from firebase import firebase
from flask import Flask, request
from forms.signup import Signup

app = Flask(__name__)
firebase = firebase.FirebaseApplication('https://my-awesome-project-13077.firebaseio.com/', None)

@app.route("/")
def hello():
  return '<h1>Hello, world!</h1>'

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
	if request.method == 'GET':
		return "this is a get method"
	else:
		form = Signup()	
		if form.validate_on_submit():
			putData = {'name' : form.name.data}
			result = firebase.post('/users', putData)
			print(result)
	return "ok" 

if __name__ == "__main__":
    app.run(debug=True)
