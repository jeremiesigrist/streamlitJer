FROM python:3.11.6
COPY . /app
WORKDIR /app

# Installe les packages du système définis dans packages.txt
RUN apt-get update && \
    apt-get install -y --no-install-recommends $(cat packages.txt | xargs) && \
    rm -rf /var/lib/apt/lists/*

# Installe les bibliothèques Python définies dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "Home.py", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false", "--server.port", "8505", "--theme.base", "dark"]