FROM mambaorg/micromamba:1.5.6

# Setze Arbeitsverzeichnis
WORKDIR /app

# Lockfile kopieren
COPY conda-linux-64.lock .

# Umgebung installieren aus dem Lockfile (conda-lock kompatibel)
RUN micromamba create --name mein_env --file conda-linux-64.lock -y

# Aktivierungs-Pfad setzen
ENV MAMBA_DOCKERFILE_ACTIVATE=1
SHELL ["/bin/bash", "-c"]

# spaCy-Modelle installieren
RUN micromamba run -n mein_env python -m spacy download en_core_web_sm && \
    micromamba run -n mein_env python -m spacy download en_core_web_md

# App-Dateien kopieren
COPY . .

# Ollama installieren und Modell laden
ADD https://ollama.com/install.sh /tmp/install_ollama.sh
RUN bash /tmp/install_ollama.sh && \
    ollama serve & \
    sleep 5 && \
    ollama pull phi4-mini && \
    pkill ollama

# Ports freigeben
EXPOSE 8501 11434

# Supervisor installieren
RUN micromamba install -n mein_env -c conda-forge supervisor -y

# Supervisor-Konfig kopieren
COPY supervisord.conf /etc/supervisord.conf

# Starten mit supervisord
CMD ["/opt/conda/envs/mein_env/bin/supervisord", "-c", "/etc/supervisord.conf"]
