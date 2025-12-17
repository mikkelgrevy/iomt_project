from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import time

app = Flask(__name__)

# URL til din backend API
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
        name = request.form.get('name')
        dob = request.form.get('dob')

        patient_data = {
            "name": name,
            "dob": dob
        }

        try:
            response = requests.post(f"{BACKEND_URL}/patients/", json=patient_data)
            
            if response.status_code == 201:
                return redirect(url_for('patienter'))
            else:
                return f"Fejl ved oprettelse: {response.text}", 400

        except requests.exceptions.RequestException as e:
            return f"Kunne ikke forbinde til backend: {e}", 500

    return render_template('create_patient.html')

@app.route('/create_plan', methods=['GET', 'POST'])
def create_plan():
    patients_list = []
    error_message = None

    try:
        response = requests.get(f"{BACKEND_URL}/patients/")
        if response.status_code == 200:
            patients_list = response.json()
        else:
            error_message = f"Kunne ikke hente patienter (Status {response.status_code})"
    except requests.exceptions.RequestException as e:
        error_message = f"Kunne ikke forbinde til backend: {e}"

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        medication_name = request.form.get('medication_name')
        dosage = request.form.get('dosage')
        schedule_time_str = request.form.get('schedule_time') 

        try:
            schedule_time = time.fromisoformat(schedule_time_str)
        except ValueError:
            return "Ugyldigt tidsformat. Brug HH:MM.", 400

        plan_data = {
            "patient_id": patient_id,
            "medication_name": medication_name,
            "dosage": dosage,
            "schedule_time": schedule_time.isoformat() # Send som ISO format streng
        }

        try:
            response = requests.post(f"{BACKEND_URL}/plans/", json=plan_data)
            if response.status_code == 201:
                return redirect(url_for('patienter'))
            else:
                return f"Fejl ved oprettelse af plan: {response.text}", 400
        except requests.exceptions.RequestException as e:
            return f"Kunne ikke forbinde til backend: {e}", 500

    return render_template('create_plan.html', patients=patients_list, error=error_message)


@app.route('/statistik')
def statistik():
    stats_data = None
    error_message = None
    patient_id = 2 

    try:
        response = requests.get(f"{BACKEND_URL}/stats/{patient_id}")
        if response.status_code == 200:
            stats_data = response.json()
        else:
            error_message = f"Kunne ikke hente statistik (Status {response.status_code})"
    except requests.exceptions.RequestException as e:
        error_message = f"Kunne ikke forbinde til backend: {e}"

    return render_template('statistik.html', stats=stats_data, error=error_message)
