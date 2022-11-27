from flask import render_template, request, send_from_directory, redirect
from app.flask_app import app
import os
import shutil
import datetime
import requests
import pandas as pd

# All of the html files were supposed to be inherited from the index html file, which would have contained a task bar
# on the top of the screen. That never got to be, because my html and especially css skills were too novice

# This would have been better stored in a config file then parsed with a config parser, this never should be directly
# in the code
URL = 'http://35.180.98.32:8000'


@app.route('/')
def route():
    """
    Renders a html, containing the home screen
    :return: rendered html
    """
    return render_template('index.html')


@app.route('/about')
def about():
    """
    Renders a html, containing the home screen (again)
    Supposed to be a section regarding the project and explaining some things to the user
    However I never got to that
    :return:
    """
    return render_template('index.html')


@app.route('/upload', methods=["GET", "POST"])
def upload():
    """
    Method responsible for receiving multiple jpg files from the users
    It zips them and sends them over to the AI model server, which then processes them
    And sends back a dictionary object containing the predictions
    :return:
    """
    if request.method == "POST":

        if request.files:
            # Gets a list of all the file storage items (images)
            images = request.files.getlist('images')
            temp_folder = os.path.join(os.getcwd(), 'app', 'temp')

            # Only allow jpg to be sent to the AI model, the FileStorage object has limited functionally
            # which does not allow for easy conversion from other popular formats like png, etc.
            for image in images:
                if image.filename.endswith('.jpg'):
                    image.save(os.path.join(temp_folder, image.filename))

            # Gets the current timestamp and attaches it to the zip file to ensure that the
            # file deleted later is the one created
            # This was meant as a measure for when I implement the app as a async quart app,
            # however it never came to that
            curr_time = datetime.datetime.now()
            timestamp = curr_time.timestamp()
            zip_name = 'temp_{}'.format(str(timestamp))

            shutil.make_archive(zip_name, 'zip', temp_folder)

            # clean up temp folder
            for file in os.listdir(temp_folder):
                os.remove(os.path.join(temp_folder, file))

            # Send over to the model
            # If there is nothing send back from the AI model, fail silently and redirect the user
            # to the same flask app URL
            url = f'{URL}/analyze_hook'
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


def write_to_csv(results_dic) -> None:
    """
    :param results_dic: takes in a dictionary objects and writes a csv to the file system
    :return: None
    """
    results_list = [[k.capitalize(), v] for k, v in results_dic.items()]
    print(results_list)
    df = pd.DataFrame(results_list)
    df.to_csv('biodiversity_analysis.csv', index=False)
