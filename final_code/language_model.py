import requests

def check_if_text_has_outbreak(text):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": 
                """Im folgenden erhältst du einen Text. Ich möchte, dass du diesen Text daraufhin analysierst, ob es einen Krankheits
                Ausbruch gegeben hat. Falls ja, gib bitte "True" zurück, falls nicht, gib "False" zurück. Hier der Text: """ + text,
            "stream": False
        }
    )
    return response.json()["response"]

def extract_outbreak_place(text):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": 
                """Im folgenden erhältst du einen Text. Bitte untersuche diesen Text daraufhin an welchem Ort es einen Ausbruch
                 der Krankheit gegeben hat. Gib bitte ausschließlich den Ort zurück. Wenn es mehrere Ort gibt, gib sie mit
                  einem Semikolon getrennt an. Wenn kein Ort spezifiziert ist gib bitte N/A zurück. Hier der Text: """ + text,
            "stream": False
        }
    )
    return response.json()["response"]