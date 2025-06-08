# Offizielles Miniconda-Image
FROM continuumio/miniconda3

# Vermeide Interaktivität bei Installationen
ARG DEBIAN_FRONTEND=noninteractive

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    git curl wget sudo lsb-release gnupg ca-certificates bzip2 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Conda Lockfile kopieren und Umgebung installieren
COPY conda-linux-64.lock ./

# conda-lock installieren und Umgebung aus Lockfile erstellen
RUN conda install -y -c conda-forge conda-lock && \
    conda-lock install --name mein_env conda-linux-64.lock

# Standardpfad auf die neue Umgebung setzen
ENV PATH=/opt/conda/envs/mein_env/bin:$PATH

# pip aktualisieren und ensurepip ausführen
RUN conda run -n mein_env python -m ensurepip && \
    conda run -n mein_env pip install --upgrade pip

# Arbeitsverzeichnis setzen
WORKDIR /app
COPY . .

# spaCy Sprachmodelle installieren
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download en_core_web_md

# --------------------------------
# OLLAMA installieren und Modell holen
# --------------------------------
ADD https://ollama.com/install.sh /tmp/install_ollama.sh
RUN sh /tmp/install_ollama.sh

# Ollama-Server starten, Modell laden, dann beenden
RUN ollama serve & \
    sleep 5 && \
    ollama pull phi4-mini && \
    pkill ollama

# Ports freigeben (z. B. für Streamlit und Ollama)
EXPOSE 8501 11434

# Supervisor installieren (für Multi-Service-Start)
RUN conda install -n mein_env -y -c conda-forge supervisor

# Supervisor-Konfiguration hinzufügen
COPY supervisord.conf /etc/supervisord.conf

# Startbefehl über Supervisor
CMD ["/opt/conda/envs/mein_env/bin/supervisord", "-c", "/etc/supervisord.conf"]
