from flask import Flask, redirect, request, jsonify, render_template
import random
import string
import mysql.connector

app = Flask(__name__)

# MySQL Configuration (Replace with your credentials)
MYSQL_HOST = "localhost"
MYSQL_USER = "ify"
MYSQL_PASSWORD = "Akuify2018@"
MYSQL_DATABASE = "url_shortener"  # Create this database


def create_db():
    try:
        mydb = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        mycursor = mydb.cursor()

        mycursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                short_url VARCHAR(255) PRIMARY KEY,
                original_url TEXT NOT NULL
            )
        ''')

        mydb.commit()
        mydb.close()
        print("Table Created successfully")
    except mysql.connector.Error as err:
        if err.errno == 1049:
            print("Database doesn't exist")
        else:
            print(f"Something went wrong: {err}")

create_db()

def generate_short_url(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  # Render the HTML template

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form.get('original_url')
    if not original_url:
        return render_template('index.html', error='Original URL is required')

    short_url = generate_short_url()

    try:
        mydb = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        mycursor = mydb.cursor()

        mycursor.execute("INSERT INTO urls (short_url, original_url) VALUES (%s, %s)", (short_url, original_url))
        mydb.commit()
        mydb.close()

        shortened_url = request.base_url + '/' + short_url
        return render_template('index.html', shortened_url=shortened_url)

    except mysql.connector.IntegrityError:
        return shorten_url()
    except mysql.connector.Error as err:
        print(f"Something went wrong: {err}")
        return render_template('index.html', error='An error occurred')

@app.route('/<short_url>')
def redirect_to_original(short_url):
    try:
        mydb = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        mycursor = mydb.cursor()

        mycursor.execute("SELECT original_url FROM urls WHERE short_url = %s", (short_url,))
        result = mycursor.fetchone()
        mydb.close()

        if result:
            original_url = result[0]
            return redirect(original_url, code=302)
        else:
            return render_template('index.html', error='Short URL not found')
    except mysql.connector.Error as err:
        print(f"Something went wrong: {err}")
        return render_template('index.html', error='An error occurred')

if __name__ == '__main__':
    app.run(debug=True)