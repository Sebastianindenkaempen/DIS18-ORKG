#!/bin/bash

# Name für dein Environment
ENV_NAME=".venv_dis18_project"

echo "Creating virtual environment in $ENV_NAME ..."
python3 -m venv $ENV_NAME

echo "Activating virtual environment ..."
source $ENV_NAME/bin/activate

echo "Installing dependencies from requirements.txt ..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment setup complete!"
echo ""

# Wechsel in final_code
cd final_code || { echo "Ordner 'final_code' nicht gefunden!"; exit 1; }

echo "Starting Streamlit app ..."
streamlit run user_interface.py