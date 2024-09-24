
import csv
import pandas as pd
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Configureer Azure Key Vault
key_vault_name = "PortfolioRyanKeyVault"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Functie om een geheim op te halen uit Azure Key Vault
def get_secret(secret_name):
    secret = secret_client.get_secret(secret_name)
    return secret.value

# Haal de databasegegevens op uit Key Vault
host = get_secret('DBHost')  # Haal de waarde op van de geheimnaam 'DBHost'
database = get_secret('DBDatabase')  # Haal de waarde op van de geheimnaam 'DBDatabase'
username = get_secret('DBUser')  # Haal de waarde op van de geheimnaam 'DBUser'
password = get_secret('DBPasswordDollar')  # Haal de waarde op van de geheimnaam 'DBPassword'
secret_key = get_secret('SecretKey')  # Haal de waarde op van de geheimnaam 'SecretKey'

# Maak een Flask-applicatie
app = Flask(__name__)

# Stel de secret key in voor Flask
app.config['SECRET_KEY'] = secret_key 

# Functie om een verbinding met de MySQL database te maken
def get_db_connection():
    return mysql.connector.connect(
        host=host,
        database=database,
        user=username,
        password=password
    )

# Route voor de homepage (index.html)
@app.route('/')
def homepage():
    return render_template('index.html')

# Route voor dynamische pagina's zoals about.html of contact.html
@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

# Route om formuliergegevens te verwerken en op te slaan in een CSV-bestand
@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        data = request.form.to_dict()  # Zet de formuliergegevens om in een woordenboek
        write_to_csv(data)  # Schrijf de gegevens naar een CSV-bestand
        return redirect('/thankyou.html')  # Redirect naar een bedankpagina
    return 'Something went wrong!'

# Functie om formuliergegevens naar een CSV-bestand te schrijven
def write_to_csv(data):
    with open('database.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([data.get('email'), data.get('subject'), data.get('message')])

# Functie om persoonlijke informatie uit de MySQL-database op te halen
def get_personal_info():
    try:
        connection = get_db_connection()  # Maak verbinding met de MySQL-database
        cursor = connection.cursor(dictionary=True)  # Gebruik dictionary voor kolomnamen
        query = "SELECT * FROM personal"  # SQL-query om alle records uit de 'personal' tabel op te halen
        cursor.execute(query)
        rows = cursor.fetchall()  # Haal alle rijen op
        df = pd.DataFrame(rows)  # Zet de resultaten om in een pandas DataFrame
        cursor.close()
        connection.close()
        return df  # Geef de DataFrame terug voor weergave in HTML
    except mysql.connector.Error as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()  # Als er een fout is, retourneer een lege DataFrame

# Functie om persoonlijke informatie in de MySQL-database in te voegen
def insert_personal_info(first_name, last_name, hobby):
    try:
        connection = get_db_connection()  # Maak verbinding met de database
        cursor = connection.cursor()  # Creëer een cursor voor het uitvoeren van queries
        query = """
            INSERT INTO personal (first_name, last_name, hobby)
            VALUES (%s, %s, %s)
        """  # SQL-query om gegevens in de 'personal' tabel in te voegen
        cursor.execute(query, (first_name, last_name, hobby))  # Voer de query uit met de opgegeven waarden
        connection.commit()  # Sla de wijzigingen op
        cursor.close()
        connection.close()
        print("Data inserted successfully.")
        return True  # Geef True terug als het succesvol is
    except mysql.connector.Error as e:
        print(f"Error inserting data: {e}")
        return False  # Geef False terug als er een fout optreedt

# Route voor het verwerken en weergeven van persoonlijke informatie
@app.route('/personal.html', methods=['GET', 'POST'])
def personal():
    if request.method == 'POST':
        # Haal de form data op bij een POST-verzoek
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        hobby = request.form.get('hobby')

        print(f"Received POST data: first_name={first_name}, last_name={last_name}, hobby={hobby}")

        # Probeer de gegevens toe te voegen aan de database
        if insert_personal_info(first_name, last_name, hobby):
            flash('Personal information added successfully!', 'success')
        else:
            flash('Failed to add personal information.', 'error')

        # Na het POST-verzoek, redirect naar de 'personal' pagina om de GET-functie aan te roepen
        return redirect(url_for('personal'))

    # Haal de gegevens op bij een GET-verzoek en geef deze weer
    df = get_personal_info()
    table_html = df.to_html(classes='table table-striped')
    return render_template('personal.html', table_html=table_html)


# Start de Flask-app op poort 3000
if __name__ == '__main__':
    app.run(port=3000)
