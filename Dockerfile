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

# Conda Umgebung aus environment.yml
COPY environment.yml .
RUN conda env create -f environment.yml
ENV PATH=/opt/conda/envs/mein_env/bin:$PATH

# Arbeitsverzeichnis setzen
WORKDIR /app
COPY . .

# --------------------
# OLLAMA installieren
# --------------------
# GPG Key und Repository hinzufügen
RUN curl -fsSL https://ollama.com/install.sh | sh

# Modell vorab laden (optional: spart Wartezeit beim Start)
RUN ollama serve & \
    sleep 5 && \
    ollama pull phi4-mini && \
    pkill ollama

# Ports freigeben
EXPOSE 8501 11434

# Supervisord installieren für Multi-Service-Start
RUN pip install supervisor

# Supervisor-Konfiguration hinzufügen
COPY supervisord.conf /etc/supervisord.conf

# Startet Ollama + Streamlit parallel
CMD ["/opt/conda/envs/mein_env/bin/supervisord", "-c", "/etc/supervisord.conf"]
