from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, select, Boolean
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
# Initialize Migrate
migrate = Migrate(app, db)

user = None

# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


with app.app_context():
    db.create_all()


def save(name, email, password):
    try:
        user_to_create = User(name=name, email=email, password=password)
        db.session.add(user_to_create)
        db.session.commit()
        return True
    except Exception as e:
        print(f'Error saving user with email {email}:  {e}')
    finally:
        db.session.close()
    return False


def find_by_email(email):
    try:
        stmt = select(User).where(User.email == email)
        result = db.session.execute(stmt).scalar_one_or_none()
        if result:
            return result
        else:
            print(f'User with email {email} not found.')
    except Exception as e:
        print(f'Error finding User with email {email}:  {e}')
    finally:
        db.session.close()
    return False


@app.route('/')
def home():
    return render_template("index.html")


"""
    http://127.0.0.1:5000/register?name=jessie&email=jj%40gmail.com&password=MyPassword
    cannot be handled the conventional way like below because we are dealing with forms:
        name = request.args.get('name')
        email = request.args.get('email')
        password = request.args.get('password')
    the above only works if the values are embedded in the URL
"""
@app.route('/register', methods=['GET','POST'])
def register():
    # receive the data
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        print(f'name:  {name}, email:  {email}, password:  {password}')
        # hash the password
        hashed_output = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        outcome = save(name, email, hashed_output)
        if outcome:
            return render_template("secrets.html", name=name)
    elif request.method == "GET":
        print('unhandled for now')
    return render_template("register.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        error = 'Invalid login credentials.'
        email = request.form.get('email')
        password = request.form.get('password')
        current_user = find_by_email(email)
        if current_user:
            if check_password_hash(current_user.password, password):
                login_user(current_user)
                return redirect(url_for('secrets', logged_in = current_user.is_authenticated))
            else:
                flash(error)
                return render_template("login.html", logged_in = current_user.is_authenticated)
        else:
            flash(error)
            return render_template("login.html", logged_in = current_user.is_authenticated)
    else:
        print(f'Recursive')
        return render_template("login.html", logged_in = False)


@app.route('/secrets')
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    pass


"""
can also be coded as below:
return send_from_directory('static', path="files/cheat_sheet.pdf")
"""
@app.route('/download')
def download():
    # return send_from_directory('static/files', 'cheat_sheet.pdf', as_attachment=True)
    return send_from_directory('static', path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
