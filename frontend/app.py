from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patienter')
def patienter():
    patients_list = []
    error_message = None

    try:
        response = requests.get(f"{BACKEND_URL}/patients/")
        if response.status_code == 200:
            patients_list = response.json
        else:
            error_message = f"Kunne ikke forbinde til backend - Error code {response.status_code}"
    except: requests.exceptions.RequestException as e:
        error_message = f"Kunne ikke forbinde til backend - Error code {e}"
        print(error_message)

    return render_template('patienter.html, patients=patients_list, error=error_message')
