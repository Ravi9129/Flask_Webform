from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# PostgreSQL URI configuration (Replace with your actual credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'  # Update with your PostgreSQL details
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking (for performance)

# Initialize the database
db = SQLAlchemy(app)

# Define the User model for PostgreSQL database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Define Flask-WTF form for user registration
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
        
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create a new User object
        new_user = User(name=name, email=email, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to dashboard after successful registration
        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
