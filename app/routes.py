from flask import render_template, request, send_from_directory, redirect
from app.flask_app import app
import os
import shutil
import datetime
import requests
import pandas as pd


@app.route('/')
def route():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('index.html')


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":

        if request.files:

            # Set as an attribute in the html
            images = request.files.getlist('images')
            temp_folder = os.path.join(os.getcwd(), 'app', 'temp')
            for image in images:
                if image.filename.endswith('.jpg'):
                    image.save(os.path.join(temp_folder, image.filename))

            curr_time = datetime.datetime.now()
            timestamp = curr_time.timestamp()
            zip_name = 'temp_{}'.format(str(timestamp))

            shutil.make_archive(zip_name, 'zip', temp_folder)

            # clean up temp folder
            for file in os.listdir(temp_folder):
                os.remove(os.path.join(temp_folder, file))

            # Send over to the model
            url = 'http://35.180.98.32:8000/analyze_hook'
            redirect_flag = True
            with open(os.path.join(os.getcwd(), zip_name + ".zip"), 'rb') as zip_file:
                req = requests.post(url, files={'file': zip_file.read()})
                results = req.json()
                if results:
                    write_to_csv(results)
                    redirect_flag = False

            os.remove(os.path.join(os.getcwd(), zip_name + ".zip"))
            if redirect_flag:
                return redirect(request.url)

            return send_from_directory(directory=os.getcwd(), path='biodiversity_analysis.csv', as_attachment=True)

    return render_template('upload.html')


def write_to_csv(results_dic):
    results_list = [[k.capitalize(), v] for k, v in results_dic.items()]
    print(results_list)
    df = pd.DataFrame(results_list)
    df.to_csv('biodiversity_analysis.csv', index=False)
