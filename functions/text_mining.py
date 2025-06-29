import requests
import spacy
import pandas as pd
from spacy.matcher import PhraseMatcher


def summarize_outbreak(text: str) -> str:
    
    """
    Sends a prompt to a local LLM (phi4-mini) to extract outbreak-related 
    locations and dates from a given text.

    Returns a concise summary describing where and when outbreaks occurred.
    """

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


def extract_location(text: str) -> str | None:
    
    """
    Extracts location names from text using spaCy.

    Returns a comma-separated string or None if no locations found.
    """

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    return ", ".join(locations) if locations else None


def extract_date(text: str) -> str | None:
    
    """
    Extracts date expressions from text using spaCy.

    Returns a comma-separated string or None if no dates found.
    """

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    return ", ".join(dates) if dates else None


def extract_outbreak_info(df: pd.DataFrame, text_column: str = "full-text") -> pd.DataFrame:

    """
    Extracts outbreak-related locations and dates from texts using spaCy and PhraseMatcher.
    Adds two new columns: 'outbreak_locations' and 'outbreak_dates'.
    """
    
    nlp = spacy.load("en_core_web_md")

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    phrases = [
        'has caused', 'outbreak', 'outbreaks', ' virus detections', 'detection', 'reported', 'emergence', 'have been identified', 'occured in', 
        'cases', 'epizootic waves', 'detected in', 'emerged in'
        'mortality event' # TODO: challengen
    ]
    patterns = [nlp.make_doc(p) for p in phrases]
    matcher.add("OUTBREAK", patterns)

    # Helper function - filters negations
    def is_negated(span):
        for token in span.root.head.subtree:
            if token.dep_ == "neg":
                return True
        return False
    
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

        outbreak_locations.append(", ".join(locations) if locations else "")
        outbreak_dates.append(", ".join(dates) if dates else "")

    df["outbreak_locations"] = outbreak_locations
    df["outbreak_dates"] = outbreak_dates
    return df