#!/usr/bin/env bash
set -e
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask
echo "==============================================="
echo "Starting Enhanced Security Education Lab"
echo "==============================================="
echo "Access the application at: http://127.0.0.1:5000/"
echo "Default admin credentials: admin / admin123"
echo "Default user credentials: alice / alice123, bob / bob123"
echo "==============================================="
python app.py