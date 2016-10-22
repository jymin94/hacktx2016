from firebase import firebase
from flask import Flask
# from .forms import FirePut

app = Flask(__name__)
firebase = firebase.FirebaseApplication('https://my-awesome-project-13077.firebaseio.com/', None)

@app.route("/")
def hello():
  return '<h1>Hello, world!</h1>'

if __name__ == "__main__":
    app.run(debug=True)
