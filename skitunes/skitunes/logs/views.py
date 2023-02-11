from flask import current_app, redirect, render_template, Response, request, session, url_for, send_file
import logging
import os
from skitunes import app

# Flask view to list all reports in the directory
@app.route("/Reports")
def view_reports():
    prefix = os.getcwd()
    # Set the files as everything in the directory
    files = os.listdir(prefix + '/log/')
    # Return the reports.html file with all the files and set our Filter to None
    return render_template('reports.html', files=files, filter=None)

# Flask view to view the individual report in the UI
@app.route("/Reports/<filename>")
def view_report(filename):
    prefix = os.getcwd()
    # Open the report file
    with open(prefix + '/log/' + filename, "r") as report:
        # Read the report and save it as a string
        string = report.read()
    # Return the report.html with the file being the strign read of the file
    return render_template('report.html', file=string, filename=filename)

# Flask view to download the file
@app.route("/Reports/download/<filename>", methods=['GET', 'POST'])
def download_report(filename):
    # Set the path of the file
    prefix = os.getcwd()
    path = prefix + '/log/' + filename
    # Return the file with send file, as a csv attachment
    return send_file(path,  as_attachment=True)