from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patienter')
def patienter():
    return render_template('patienter.html')