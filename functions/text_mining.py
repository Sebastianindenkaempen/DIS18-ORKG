import requests
import spacy
from spacy.matcher import PhraseMatcher


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