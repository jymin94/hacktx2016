from firebase import firebase
from flask import * 

app = Flask(__name__)
firebase = firebase.FirebaseApplication('https://my-awesome-project-13077.firebaseio.com/', None)

@app.route("/")
def hello():
	return render_template('index.html')

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
	if request.method == 'GET':
		return "this is a get method"
	return "ok"
	# else:
		# name = request.form["name"]
		# result = firebase.put('/users', 'name', name)
		# return name
	# return "ok" 

# TODO authentication check before changing database

if __name__ == "__main__":
    app.run(debug=True)
