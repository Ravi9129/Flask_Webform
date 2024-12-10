from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import bcrypt
import pyodbc

app = Flask(__name__)

# MSSQL Database configuration
app.config['MSSQL_SERVERNAME'] = 'your_server_name'  # Update with your server name
app.config['MSSQL_DATABASE'] = 'your_database_name'  # Update with your database name
app.config['MSSQL_USERNAME'] = 'your_username'  # Update with your database username
app.config['MSSQL_PASSWORD'] = 'your_password'  # Update with your database password
app.secret_key = 'your_secret_key'  # Add a secret key for CSRF protection

# Connect to MSSQL database using pyodbc
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={app.config["MSSQL_SERVERNAME"]};'
        f'DATABASE={app.config["MSSQL_DATABASE"]};'
        f'UID={app.config["MSSQL_USERNAME"]};'
        f'PWD={app.config["MSSQL_PASSWORD"]}'
    )
    return conn

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database using pyodbc
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password.decode('utf-8'))
            )
            conn.commit()  # Commit the transaction
            cursor.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard after successful registration
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('register'))  # Stay on the register page if there is an error

    return render_template('register.html', form=form)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
