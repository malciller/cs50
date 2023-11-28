from flask import Flask, render_template, url_for, flash, redirect, session
from forms import RegistrationForm, LoginForm, APIKeyForm
import sqlite3
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = '123' 

@app.route("/")
def home():
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Connect to the database
        conn = sqlite3.connect('info.db')
        cursor = conn.cursor()

        # Query the database for the user
        cursor.execute("SELECT * FROM users WHERE username = ?", (form.username.data,))
        user = cursor.fetchone()

        if user and hashlib.sha256(form.password.data.encode()).hexdigest() == user[2]:  # Assuming password is the third field
            session['user_id'] = user[0]   # Assuming user ID is the first field

            # Check if user has an associated key
            cursor.execute("SELECT * FROM keys WHERE user_id = ?", (session['user_id'],))
            key_exists = cursor.fetchone()

            # Close the database connection
            conn.close()

            if key_exists:
                flash('You have been logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('API Key is required.', 'info')
                return redirect(url_for('key_collection'))  # Redirect to key collection page
        else:
            flash('Login failed. Please check your username and password.', 'danger')

        # Close the database connection if login fails
        conn.close()

    return render_template('login.html', title='Login', form=form)


@app.route("/key_collection", methods=['GET', 'POST'])
def key_collection():
    form = APIKeyForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')  # Retrieve user ID from session

        if user_id:
            # Hash the API key
            hashed_api_key = hashlib.sha256(form.api_key.data.encode()).hexdigest()

            # Connect to the database
            conn = sqlite3.connect('info.db')
            cursor = conn.cursor()

            # Insert the hashed API key into the keys table
            cursor.execute("INSERT INTO keys (user_id, openai_api_key) VALUES (?, ?)", (user_id, hashed_api_key))
            conn.commit()
            conn.close()

            flash('API Key saved successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('User not identified.', 'danger')
            return redirect(url_for('login'))

    return render_template('key_collection.html', title='API Key Collection', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Connect to the database
        conn = sqlite3.connect('info.db')
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (form.username.data,))
        if cursor.fetchone():
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            # Hash the password
            hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
            
            # Add user to the database
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (form.username.data, hashed_password))
            conn.commit()

            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))

        # Close the database connection
        conn.close()

    return render_template('register.html', title='Register', form=form)



@app.route("/index", methods=['GET', 'POST'])
def index():
    # Dummy data for testing
    user_info = {
        "username": "JohnDoe",
        "email": "johndoe@example.com"
    }
    return render_template('index.html', username=user_info['username'], email=user_info['email'])




if __name__ == '__main__':
    app.run(debug=True)
