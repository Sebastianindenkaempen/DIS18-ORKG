# DIS18-ORKG

## How to use this repository
1. Clone this repository
2. Navigate into this repository using the command line `cd ./DIS18-ORKG`
3. Build the docker image by running: `docker build -t outbreak-analyzer .` (If it does not work, try `docker build --platform linux/amd64 -t outbreak-analyzer .`)
4. Start the container by using `docker run -p 8501:8501 -p 11434:11434 outbreak-analyzer`
5. Open http://localhost:8501/ in your Browser


## Topic
Extracting data about time and place of outbreaks from diseases e.g. ehec, avian influenza.

Source:
- PubMed: https://www.ncbi.nlm.nih.gov/books/NBK25501/ 
- PubMed Central: https://pmc.ncbi.nlm.nih.gov/tools/developers/

### PubMed API
The pubmed api contains three different components:
- **ESearch:** searches articles and returns pubmed article ids URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
- **ESummary:** finds and returns metadata for articles. Input could be the article IDs from ESearch. URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
- **EFetch:** returns abstracts and full texts. URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi

Source: https://www.ncbi.nlm.nih.gov/books/NBK25500/

Sources Text Mining: https://pmc.ncbi.nlm.nih.gov/tools/textmining/ 


### Text Mining Ideas

```
import nltk 
import spaCy

```

### ORKG 
- CSV Upload: https://orkg.org/help-center/article/16/Import_CSV_files_in_ORKG 

## Repo structure 
### Folder final_code    
Contains tested functions, that can be called
### Folder playground
Contains code that is in developement or not yet tested


## Anleitung zur Installation und Nutzung von Ollama

### 1. Downloading Ollama
- Besuche [Ollama Download](https://ollama.com/download) und lade den Installer herunter.
- Führe `OllamaSetup.exe` aus.

### 2. Downloading Mistral
- Öffne die Eingabeaufforderung (cmd).
- Führe den Befehl `ollama` aus, um zu überprüfen, ob die Installation erfolgreich war.
- Führe den Befehl `ollama run mistral` aus, um Mistral herunterzuladen.
- Du kannst jetzt in der Eingabeaufforderung (cmd) arbeiten oder das LLM über VS Code nutzen.

### 3. Ollama starten
- Falls Ollama nicht läuft, verwende den Befehl `ollama serve`.
- Ollama läuft auf [http://localhost:11434](http://localhost:11434).

