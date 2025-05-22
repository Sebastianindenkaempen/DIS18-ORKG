import requests
import spacy

def check_if_text_has_outbreak(text):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:1b",
            "prompt": 
        f"""
        Analysiere den folgenden Text:

        {text}

        Frage: Enthält dieser Text Informationen über einen Krankheitsausbruch?

        Antworte bitte ausschließlich mit:
        True  --> falls es Informationen über einen Krankheitsausbruch gibt
        False --> falls es keine Informationen über einen Krankheitsausbruch gibt

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
    

# def extract_outbreak_place(text):
#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "mistral",
#             "prompt": 
#                 """Im folgenden erhältst du einen Text. Bitte untersuche diesen Text daraufhin an welchem Ort es einen Ausbruch
#                  der Krankheit gegeben hat. Gib bitte ausschließlich den Ort zurück. Wenn es mehrere Ort gibt, gib sie mit
#                   einem Semikolon getrennt an. Wenn kein Ort spezifiziert ist gib bitte N/A zurück. Hier der Text: """ + text,
#             "stream": False
#         }
#     )
#     return response.json()["response"]