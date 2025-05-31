import requests
import spacy
import numpy as np
import json
import re
import pandas as pd
from spacy.matcher import PhraseMatcher

def check_if_text_has_outbreak(text):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi4-mini",
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

def regex_check_if_text_has_outbreak(text):
    pattern = r"\b(outbreak\b|epidemic\b|cases (have been|were|are)? reported in|first (was )?detected|incidence in|occurred in|emerged in|infection (has been|was)? reported)\b"
    if re.search(pattern, text, flags=re.IGNORECASE):
        return True
    else:
        return False


def summarize_outbreak(text):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi4-mini",
            "prompt": f"""
                Analyze the following abstract very carefully:

                {text}

                Task:
                Identify all disease outbreaks described in the text. For each outbreak, clearly mention the specific **location** (e.g., country, city) and the **time** it occurred. 

                Important:
                - Only include information (locations and dates) that are **directly related to the outbreak**.
                - Do **not** include any other locations or time references that are not clearly connected to an outbreak.
                - If multiple outbreaks are described, summarize each one separately.
                - The output should be a concise summary of the outbreak(s), including place and time (e.g., "An outbreak occurred in Hanoi in March 2020.").

                Do not return any additional explanation or irrelevant details.
            """,
            "stream": False
        }
    )

    return response.json()["response"].strip()


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




# Lade das spaCy-Modell nur einmal
nlp = spacy.load("en_core_web_sm")
# nlp = spacy.load("en_core_web_md")
# nlp = spacy.load("en_core_web_trf")

# Initialisiere PhraseMatcher mit relevanten Phrasen
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
phrases = [
    "outbreak", "epidemic", "cases reported in", "first detected",
    "incidence in", "occurred in", "emerged in", "infection reported"
]
patterns = [nlp.make_doc(p) for p in phrases]
matcher.add("OUTBREAK", patterns)

# Die Hauptfunktion
def extract_outbreak_info(df, text_column="full-text"):
    outbreak_locations = []
    outbreak_dates = []

    for text in df[text_column]:
        doc = nlp(text)
        locations = set()
        dates = set()

        matches = matcher(doc)
        for match_id, start, end in matches:
            sent = doc[start:end].sent
            for ent in sent.ents:
                if ent.label_ == "GPE":
                    locations.add(ent.text)
                elif ent.label_ == "DATE":
                    dates.add(ent.text)

        # Füge erkannte Infos zum Ergebnis hinzu (leere Strings, falls nichts gefunden)
        outbreak_locations.append(", ".join(locations) if locations else "")
        outbreak_dates.append(", ".join(dates) if dates else "")

    # Neue Spalten zum DataFrame hinzufügen
    df["outbreak_locations"] = outbreak_locations
    df["outbreak_dates"] = outbreak_dates
    return df

nlp = spacy.load("en_core_web_md")

# Initialisiere PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
phrases = [
    # "outbreak", "epidemic", "cases", "first detected",
    # "incidence", "emerged in", "infection reported", 
    'has caused', 'outbreak', 'outbreaks', ' virus detections', 'detection', 'reported', 'emergence', 'have been identified', 'occured in', 
    'cases', 'epizootic waves', 'detected in', 'emerged in'
    'mortality event' # TODO: challengen
]
patterns = [nlp.make_doc(p) for p in phrases]
matcher.add("OUTBREAK", patterns)

# Hilfsfunktion: prüft, ob eine Phrase negiert ist
def is_negated(span):
    for token in span.root.head.subtree:
        if token.dep_ == "neg":
            return True
    return False

# TODO: Phrases trennen bei Semikolon möglich?
# TODO: Gewissen Phrasen aussortieren z.B. Spanish Influenza? Oder 1918 insgesamt? 
# TODO: Erster reporteter Case finden von allen Krankheiten und hart rausfiltern 

# Hauptfunktion
def extract_outbreak_info(df, text_column="full-text"):
    outbreak_locations = []
    outbreak_dates = []

    for text in df[text_column]:
        doc = nlp(text)
        locations = set()
        dates = set()

        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            sent = span.sent

            # Ignoriere negierte outbreak-Phrasen
            if is_negated(span):
                continue

            for ent in sent.ents:
                if ent.label_ == "GPE":
                    locations.add(ent.text)
                elif ent.label_ == "DATE":
                    dates.add(ent.text)
                    # TODO: Pattern YYYY-YYYY wird nicht als Datum erkannt, vielleicht Regex einbauen? 

        outbreak_locations.append(", ".join(locations) if locations else "")
        outbreak_dates.append(", ".join(dates) if dates else "")

    df["outbreak_locations"] = outbreak_locations
    df["outbreak_dates"] = outbreak_dates
    return df