# Basis-Image mit Ubuntu
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    curl wget git sudo ca-certificates bzip2 \
    lsb-release gnupg python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Miniconda installieren
ENV CONDA_DIR=/opt/conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# Lockfile und Umgebung erzeugen
COPY conda-linux-64.lock ./

# conda-lock installieren (zum Erzeugen der env aus dem Lockfile)
RUN conda install -y -c conda-forge conda-lock

# Umgebung aus Lockfile erstellen (Name hier z. B. mein_env)
RUN conda-lock install --name mein_env conda-linux-64.lock
ENV PATH=/opt/conda/envs/mein_env/bin:$PATH

RUN conda run -n mein_env python -m ensurepip
RUN conda run -n mein_env pip install --upgrade pip


# Arbeitsverzeichnis setzen
WORKDIR /app
COPY . .

# spaCy Sprachmodell herunterladen
RUN python -m spacy download en_core_web_sm
# spaCy Sprachmodell herunterladen
RUN python -m spacy download en_core_web_md


# --------------------
# OLLAMA installieren
# --------------------
ADD https://ollama.com/install.sh /tmp/install_ollama.sh
RUN sh /tmp/install_ollama.sh

RUN ollama serve & \
    sleep 5 && \
    ollama pull phi4-mini && \
    pkill ollama

# Ports freigeben
EXPOSE 8501 11434

# Supervisord installieren für Multi-Service-Start
RUN conda install -n mein_env -y -c conda-forge supervisor


# Supervisor-Konfiguration hinzufügen
COPY supervisord.conf /etc/supervisord.conf

CMD ["/opt/conda/envs/mein_env/bin/supervisord", "-c", "/etc/supervisord.conf"]
