from flask import Flask, render_template, url_for, flash, redirect, session, request
from forms import RegistrationForm, LoginForm, APIKeyForm
import hashlib
from openai import OpenAI
from flask import jsonify
import config
import psycopg2
import markdown2
import re


app = Flask(__name__)
app.config['SECRET_KEY'] = '123' 
DATABASE_URI = config.DATABASE_URI


@app.route("/")
def home():
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URI)
        cursor = conn.cursor()

        # Query the database for the user
        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()

        if user and hashlib.sha256(form.password.data.encode()).hexdigest() == user[2]:  # Assuming password is the third field
            session['user_id'] = user[0]   # Assuming user ID is the first field

            # Check if user has an associated key
            cursor.execute("SELECT * FROM keys WHERE user_id = %s", (session['user_id'],))
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
        user_id = session.get('user_id')
        if user_id:
            try:
                api_key = form.api_key.data

                # Connect to the database
                conn = psycopg2.connect(DATABASE_URI)
                cursor = conn.cursor()

                # Insert the API key into the keys table
                cursor.execute("INSERT INTO keys (user_id, api_key) VALUES (%s, %s)", (user_id, api_key))
                conn.commit()
                conn.close()

                flash('API Key saved successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'An error occurred: {e}', 'danger')
        else:
            flash('User not identified.', 'danger')
            return redirect(url_for('login'))

    return render_template('key_collection.html', title='API Key Collection', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URI)
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        if cursor.fetchone():
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            # Hash the password
            hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
            
            # Add user to the database
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (form.username.data, hashed_password, form.email.data))
            conn.commit()

            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))

        # Close the database connection
        conn.close()

    return render_template('register.html', title='Register', form=form)


@app.route("/info")
def info():
    return render_template('info.html', title='Info')


@app.route("/index", methods=['GET', 'POST'])
def index():
    user_id = session.get('user_id')
    email = ''
    if user_id is None:
        # If no user is logged in, redirect to the login page
        flash('Please log in to view this page.', 'info')
        return redirect(url_for('login'))

    # Connect to the database
    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    # Query the database for the user
    cursor.execute("SELECT username, email FROM users WHERE id = %s", (user_id,))
    user_row = cursor.fetchone()

    # Close the database connection
    conn.close()

    if user_row:
        # Pass the username to the template
        return render_template('index.html', username=user_row[0], email=user_row[1])
    else:
        # Handle the case where the user is not found
        flash('User not found.', 'danger')
        return redirect(url_for('login'))


@app.route("/update_email", methods=['POST'])
def update_email():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))

    new_email = request.form['new_email']
    confirm_email = request.form['confirm_email']

    if new_email != confirm_email:
        flash('New email addresses do not match.', 'danger')
        return redirect(url_for('index'))

    # Connect to the database
    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    # Update the email in the database
    cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
    conn.commit()
    conn.close()

    flash('Email updated successfully.', 'success')
    return redirect(url_for('index'))



@app.route("/reset_password", methods=['POST'])
def reset_password():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))

    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Connect to the database
    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    # Check if the current password is correct
    cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
    stored_password = cursor.fetchone()[0]

    if stored_password != hashlib.sha256(current_password.encode()).hexdigest():
        flash('Current password is incorrect.', 'danger')
        conn.close()
        return redirect(url_for('index'))

    # Check if new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        conn.close()
        return redirect(url_for('index'))

    # Update the password in the database
    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_password, user_id))
    conn.commit()
    conn.close()

    flash('Password successfully updated.', 'success')
    return redirect(url_for('index'))


@app.route("/update_api_key", methods=['POST'])
def update_api_key():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))

    new_api_key = request.form['new_api_key']

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    cursor.execute("UPDATE keys SET api_key = %s WHERE user_id = %s", (new_api_key, user_id))
    conn.commit()
    conn.close()

    flash('API Key updated successfully.', 'success')
    return redirect(url_for('index'))



@app.route("/logout", methods=['POST'])
def logout():
    # Clear the user_id from session
    session.pop('user_id', None)

    # Redirect to login page
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route("/delete_account", methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))

    delete_username = request.form['delete_username']
    delete_password = request.form['delete_password']

    # Connect to the database
    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    # Check if the entered username and password are correct
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('User not found.', 'danger')
        conn.close()
        return redirect(url_for('index'))

    stored_username = user[1]
    stored_password = user[2]

    if delete_username != stored_username or hashlib.sha256(delete_password.encode()).hexdigest() != stored_password:
        flash('Invalid username or password.', 'danger')
        conn.close()
        return redirect(url_for('index'))

    # If the confirmation checkbox is checked, show the secondary confirmation
    if request.form.get('confirm_delete'):
        return render_template('delete_account_confirmation.html')

    # If the confirmation checkbox is not checked, redirect back to user_info
    flash('Account deletion requires confirmation. Check the confirmation box.', 'info')
    conn.close()
    return redirect(url_for('index'))




@app.route("/confirm_delete_account", methods=['POST'])
def confirm_delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))

    # Connect to the database
    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    # Delete user from the users table
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    # Delete associated keys
    cursor.execute("DELETE FROM keys WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()

    # Clear the user_id from session
    session.pop('user_id', None)

    flash('Account deleted successfully.', 'success')
    return redirect(url_for('login'))


# Handle CodeBlock
def preprocess_markdown(content):
    code_blocks = []
    placeholder_template = "<!--CODE_BLOCK_PLACEHOLDER_{}-->"

    def replace_with_placeholder(match):
        code_blocks.append(match.group(0))
        return placeholder_template.format(len(code_blocks) - 1)

    processed_content = re.sub(r'```(.*?)```', replace_with_placeholder, content, flags=re.DOTALL)
    return processed_content, code_blocks


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data['message']
    user_id = session.get('user_id')

    # Ensure user_id is available
    if not user_id:
        return jsonify({'response': 'User not authenticated.', 'response_id': None})

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    try:
        # Retrieve the user's API key from the database
        cursor.execute("SELECT api_key FROM keys WHERE user_id = %s", (user_id,))
        api_key_row = cursor.fetchone()

        if api_key_row:
            api_key = api_key_row[0]

            # Initialize the OpenAI client with the user's API key
            client = OpenAI(api_key=api_key)

            # Using chat.completions.create method
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message},
                ]
            )

            # Extracting the assistant's response correctly
            if response.choices and response.choices[0].message:
                assistant_response = response.choices[0].message.content

                # Preprocess the content to handle code blocks
                preprocessed_content, code_blocks = preprocess_markdown(assistant_response)
                html_response = markdown2.markdown(preprocessed_content)

                # Reinsert code blocks into HTML content
                for i, code_block in enumerate(code_blocks):
                    html_response = html_response.replace(f"<!--CODE_BLOCK_PLACEHOLDER_{i}-->", code_block)

                # Log user message
                cursor.execute("INSERT INTO user_messages (text, user_id) VALUES (%s, %s)", (user_message, user_id))
                conn.commit()

                # Retrieve message_id
                cursor.execute("SELECT message_id FROM user_messages WHERE text = %s AND user_id = %s ORDER BY message_id DESC LIMIT 1", (user_message, user_id))
                message_id = cursor.fetchone()[0]

                # Log chat response and get response_id
                cursor.execute("INSERT INTO chat_responses (text, message_id) VALUES (%s, %s) RETURNING response_id", (assistant_response, message_id))
                response_id = cursor.fetchone()[0]

                conn.commit()

                return jsonify({'response': html_response, 'response_id': response_id})
            else:
                return jsonify({'response': 'No response from chatbot.', 'response_id': None})
        else:
            return jsonify({'response': 'API Key not found or invalid.', 'response_id': None})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': 'Error in processing the message.', 'response_id': None})
    finally:
        conn.close()


@app.route('/mark_response_helpful', methods=['POST'])
def mark_response_helpful():
    data = request.get_json()
    response_id = data.get('response_id')

    if not response_id:
        return jsonify({'status': 'error', 'message': 'Missing response ID'}), 400

    # Connect to the database
    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    try:
        # Update the database to mark the response as helpful
        cursor.execute("UPDATE chat_responses SET is_helpful = TRUE WHERE response_id = %s", (response_id,))
        conn.commit()

        return jsonify({'status': 'success', 'message': 'Response marked as helpful'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while processing your request'})
    finally:
        conn.close()






if __name__ == '__main__':
    app.run(debug=True)
