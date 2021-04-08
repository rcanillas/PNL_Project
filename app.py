from flask import Flask
from flask import request, render_template

app = Flask(__name__)


# Page d'accueil
@app.route('/')
def hello_world():
    return "Hello, comment ça aujourd'hui ?"  # + la boîte avec le texte


@app.route('/chat')
def index():
    return render_template('form.html')


# Envoi du texte


@app.route('/send', methods=["POST", "GET"])
def hello():
    return 'Hello, Axel!'


"""@app.route("/test", methods=["GET","POST"])
def submit():
    form = ContactForm()
    if request.method == "POST":
        if request.form.get("submit_a"):
            return 'Hello, A!'
        elif request.form.get("submit_b"):
            return 'Hello, B!'
    elif request.method == "GET":
        return render_template('form.html', form=form)
"""
