# BARD/src/router.py
from flask import render_template, request, jsonify

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
