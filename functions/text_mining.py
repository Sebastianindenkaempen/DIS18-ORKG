import requests
import spacy
import numpy as np

def check_if_text_has_outbreak(text):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": 
        f"""
        Analysiere den folgenden Text sehr genau:

        {text}

        Frage: Beschreibt der Text einen Krankheitsausbruch, bei dem sowohl ein konkreter Ort (z.B. Ländername, Stadt) als auch ein konkreter Zeitpunkt (z.B. Datum, Monat/Jahr) genannt werden?

        Antworte ausschließlich mit:
        True  --> falls sowohl Ort als auch konkreter Zeitpunkt des Ausbruchs im Text genannt werden
        False --> falls Ort oder konkreter Zeitpunkt fehlen oder kein Ausbruch beschrieben wird

        Antwort:""",
            "stream": False
        }

        )
    return response.json()["response"]
    # if response.json()["response"] == "True" or response.json()["response"] == "True\n":
    #     return True
    # elif response.json()["response"] == "False" or response.json()["response"] == "False\n":
    #     return False
    # else: 
    #     return "Error - No Answer from LLM"
    
def parse_outbreak(value):
    if isinstance(value, str):
        val = value.lower()
        if 'true' in val:
            return True
        elif 'false' in val:
            return False
    return np.nan


def extract_location(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    return ", ".join(locations) if locations else None

def extract_date(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    return ", ".join(dates) if dates else None
    