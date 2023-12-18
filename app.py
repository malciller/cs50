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

# checks database and retrieves users saved messages
def get_saved_messages(user_id):
    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id, text, response_id, is_helpful, include_in_future_context
            FROM chat_responses
            WHERE user_id = %s AND include_in_future_context = TRUE
        """, (user_id,))
        messages = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching messages: {e}")
        messages = []
    finally:
        conn.close()

    return [{"sender": "ChatBot", "text": msg[1], "response_id": msg[2], "is_helpful": msg[3], "is_included": "true"} for msg in messages]



# initializes at login screen
@app.route("/")
def home():
    return redirect(url_for('login'))


# handles log ins
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = psycopg2.connect(DATABASE_URI)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()

        if user and hashlib.sha256(form.password.data.encode()).hexdigest() == user[2]:
            session['user_id'] = user[0] 

            cursor.execute("SELECT * FROM keys WHERE user_id = %s", (session['user_id'],))
            key_exists = cursor.fetchone()

            conn.close()

            if key_exists:
                flash('You have been logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('API Key is required.', 'info')
                return redirect(url_for('key_collection')) 
        else:
            flash('Login failed. Please check your username and password.', 'danger')

        conn.close()

    return render_template('login.html', title='Login', form=form)


# handles initial collection of openai api key
@app.route("/key_collection", methods=['GET', 'POST'])
def key_collection():
    form = APIKeyForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')
        if user_id:
            try:
                api_key = form.api_key.data

                conn = psycopg2.connect(DATABASE_URI)
                cursor = conn.cursor()

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


# handles creating an account
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = psycopg2.connect(DATABASE_URI)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        if cursor.fetchone():
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
            
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (form.username.data, hashed_password, form.email.data))
            conn.commit()

            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))

        conn.close()

    return render_template('register.html', title='Register', form=form)


# handles displaying user info partial template
@app.route("/info")
def info():
    return render_template('info.html', title='Info')


# handles main index page
@app.route("/index", methods=['GET', 'POST'])
def index():
    user_id = session.get('user_id')
    print (user_id)
    if user_id is None:
        flash('Please log in to view this page.', 'info')
        return redirect(url_for('login'))

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cr.text 
        FROM chat_responses cr
        JOIN user_messages um ON cr.message_id = um.message_id
        WHERE um.user_id = %s AND cr.include_in_future_context = TRUE
    """, (user_id,))
    context_messages = cursor.fetchall()

    saved_messages = get_saved_messages(user_id)

    cursor.execute("SELECT username, email FROM users WHERE id = %s", (user_id,))
    user_row = cursor.fetchone()

    conn.close()

    if user_row:
        return render_template('index.html', username=user_row[0], email=user_row[1], context_messages=context_messages, saved_messages=saved_messages)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))


# handles update email form
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

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
    conn.commit()
    conn.close()

    flash('Email updated successfully.', 'success')
    return redirect(url_for('index'))

# handles reset password form
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


# handles update api form
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


# handles log out form
@app.route("/logout", methods=['POST'])
def logout():
    session.pop('user_id', None)

    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# handles showing how to form
@app.route("/how_to", methods=['POST'])
def how_to():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))
    return redirect(url_for('how_to'))


# handles delete account form
@app.route("/delete_account", methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to perform this action.', 'danger')
        return redirect(url_for('login'))

    delete_username = request.form['delete_username']
    delete_password = request.form['delete_password']

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

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

    if request.form.get('confirm_delete'):
        return render_template('delete_account_confirmation.html')

    flash('Account deletion requires confirmation. Check the confirmation box.', 'info')
    conn.close()
    return redirect(url_for('index'))


@app.route("/confirm_delete_account", methods=['POST'])
def confirm_delete_account():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('You must be logged in to perform this action.', 'danger')
            return redirect(url_for('login'))

        # Connect to the database
        conn = psycopg2.connect(DATABASE_URI)
        cursor = conn.cursor()


        # Delete associated keys
        cursor.execute("DELETE FROM keys WHERE user_id = %s", (user_id,))

        # Delete user from the users table
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()
        conn.close()

        # Clear the user_id from session
        session.pop('user_id', None)

        flash('Account deleted successfully.', 'success')
        return redirect(url_for('login'))

    except Exception as e:
        # Log the exception e
        print("Error:", e)
        # Handle the error appropriately
        flash('An error occurred.', 'danger')
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


# handles interaction with openai API
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data['message']
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'response': 'User not authenticated.', 'response_id': None})

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT api_key FROM keys WHERE user_id = %s", (user_id,))
        api_key_row = cursor.fetchone()

        if api_key_row:
            api_key = api_key_row[0]

            cursor.execute("""
                SELECT cr.text 
                FROM chat_responses cr
                JOIN user_messages um ON cr.message_id = um.message_id
                WHERE um.user_id = %s AND cr.include_in_future_context = TRUE
            """, (user_id,))
            included_responses = cursor.fetchall()

            context_messages = [{"role": "system", "content": "You are a helpful assistant."}]
            for response in included_responses:
                context_messages.append({"role": "assistant", "content": response[0]})

            context_messages.append({"role": "user", "content": user_message})

            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=context_messages
            )

            if response.choices and response.choices[0].message:
                assistant_response = response.choices[0].message.content

                preprocessed_content, code_blocks = preprocess_markdown(assistant_response)
                html_response = markdown2.markdown(preprocessed_content)

                for i, code_block in enumerate(code_blocks):
                    html_response = html_response.replace(f"<!--CODE_BLOCK_PLACEHOLDER_{i}-->", code_block)

                cursor.execute("INSERT INTO user_messages (text, user_id) VALUES (%s, %s)", (user_message, user_id))
                conn.commit()

                cursor.execute("SELECT message_id FROM user_messages WHERE text = %s AND user_id = %s ORDER BY message_id DESC LIMIT 1", (user_message, user_id))
                message_id = cursor.fetchone()[0]

                cursor.execute("INSERT INTO chat_responses (text, message_id, user_id) VALUES (%s, %s, %s) RETURNING response_id", (assistant_response, message_id, user_id))
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


# handles user feedback button
@app.route('/mark_response_helpful', methods=['POST'])
def mark_response_helpful():
    data = request.get_json()
    response_id = data.get('response_id')

    if not response_id:
        return jsonify({'status': 'error', 'message': 'Missing response ID'}), 400

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE chat_responses SET is_helpful = TRUE WHERE response_id = %s", (response_id,))
        conn.commit()

        return jsonify({'status': 'success', 'message': 'Response marked as helpful'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while processing your request'})
    finally:
        conn.close()


# hadnles passing saved messages as context in subsequent messages
@app.route('/include_response_in_context', methods=['POST'])
def select_response_for_context():
    data = request.get_json()
    response_id = data.get('response_id')
    if not response_id:
        return jsonify({'status': 'error', 'message': 'Missing response ID'}), 400

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE chat_responses SET include_in_future_context = TRUE WHERE response_id = %s", (response_id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Response selected for future context'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while processing your request'})
    finally:
        conn.close()


# handles save message button
@app.route('/toggle_include_response', methods=['POST'])
def toggle_include_response():
    data = request.get_json()
    response_id = data.get('response_id')
    include = data.get('include')

    if response_id is None:
        return jsonify({'status': 'error', 'message': 'Missing response ID'}), 400

    conn = psycopg2.connect(DATABASE_URI)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE chat_responses SET include_in_future_context = %s WHERE response_id = %s", (include, response_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Response inclusion toggled'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while processing your request'})
    finally:
        conn.close()


# initialization of app
if __name__ == '__main__':
    app.run(debug=True)
