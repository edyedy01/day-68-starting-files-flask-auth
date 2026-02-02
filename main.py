from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
# from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
# login_manager = LoginManager()
# login_manager.init_app(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE IN DB
class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


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
        # hashed_output_split = hashed_output.split('$')
        # method = hashed_output_split[0]
        # salt = hashed_output_split[1]
        # password_hashed = hashed_output_split[2]
        password_hashed = hashed_output
        # persist the data
        outcome = save(name, email, password_hashed)
        if outcome:
            return render_template("secrets.html", name=name)
    elif request.method == "GET":
        print('unhandled for now')
    return render_template("register.html")


@app.route('/login')
def login():
    return render_template("login.html")


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
