from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

#URL til din backend API
BACKEND_URL = "http://127.0.0.1:8000"

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
            patients_list = response.json()
        else:
            error_message = f"Kunne ikke forbinde til backend - Error code {response.status_code}"

    except requests.exceptions.RequestException as e:
        error_message = f"Kunne ikke forbinde til backend: {e}"
        print(error_message)

    return render_template('patienter.html', patients=patients_list, error=error_message)

@app.route('/create_patient', methods=['GET', 'POST'])
def create_patient():
    if request.method == 'POST':
#1. Hent data fra formularen
        name = request.form.get('name')
        dob = request.form.get('dob')

#2. Forbered data til API (JSON format)
        patient_data = {
            "name": name,
            "dob": dob
        }

        try:
#3. Send POST request til backend
            response = requests.post(f"{BACKEND_URL}/patients/", json=patient_data)

            if response.status_code == 201:
#Succes! Send brugeren tilbage til patientlisten
                return redirect(url_for('patienter'))
            else:
#Fejl fra backend
                return f"Fejl ved oprettelse: {response.text}", 400

        except requests.exceptions.RequestException as e:
            return f"Kunne ikke forbinde til backend: {e}", 500

#Hvis det er et GET request (brugeren besøger siden), vis formularen
    return render_template('create_patient.html')