# Gebruik Python-image als basis
FROM python:3.9-slim

# Stel de werkdirectory in de container in
WORKDIR /app

# Kopieer het requirements-bestand naar de werkdirectory
COPY requirements.txt .

# Installeer de benodigde Python-pakketten
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de applicatiecode naar de werkdirectory
COPY . .

# Stel de omgeving variabelen in voor Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Open de poort die door de container gebruikt zal worden
EXPOSE 3000

# Definieer het commando dat wordt uitgevoerd wanneer de container start
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]
