from flask import render_template, request, redirect, jsonify, make_response
from app.flask_app import app
import os

@app.route('/')
def route():
    return "Hi there"


@app.route('/about')
def about():
    return render_template('index.html')


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":

        if request.files:

            # Set as an attribute in the html
            image = request.files["image"]
            print(image)

            return redirect(request.url)
    return render_template('upload.html')

