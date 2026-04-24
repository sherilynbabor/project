from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

# ---------------- APP SETUP ----------------
app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_fallback_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agriyu.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db = SQLAlchemy(app)

# ---------------- LOGIN ----------------
login_manager = LoginManager(app)
login_manager.login_view = "login"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ---------------- MODELS ----------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    crops = db.relationship("Crop", backref="owner", cascade="all, delete", lazy=True)


class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100))
    notes = db.Column(db.Text)
    image = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ---------------- HELPERS ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        if len(username) < 3 or len(password) < 4:
            flash("Username or password too short", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(username=username, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials", "error")
            return redirect(url_for("login"))

        login_user(user)
        flash("Welcome back!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    if request.method == "POST":
        name = request.form.get("name")
        status = request.form.get("status")
        notes = request.form.get("notes")
        file = request.files.get("image")

        if not name:
            flash("Crop name is required", "error")
            return redirect(url_for("dashboard"))

        image_name = None

        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("Invalid file type", "error")
                return redirect(url_for("dashboard"))

            # UNIQUE filename (fix overwrite bug)
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            image_name = filename

        crop = Crop(
            name=name,
            status=status,
            notes=notes,
            image=image_name,
            owner=current_user
        )

        db.session.add(crop)
        db.session.commit()

        flash("Crop added!", "success")
        return redirect(url_for("dashboard"))

    crops = Crop.query.filter_by(user_id=current_user.id).order_by(Crop.id.desc()).all()

    return render_template("dashboard.html", crops=crops)


# DELETE
@app.route("/delete/<int:crop_id>", methods=["POST"])
@login_required
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)

    if crop.owner != current_user:
        flash("Unauthorized action", "error")
        return redirect(url_for("dashboard"))

    if crop.image:
        try:
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], crop.image))
        except FileNotFoundError:
            pass

    db.session.delete(crop)
    db.session.commit()

    flash("Deleted successfully", "success")
    return redirect(url_for("dashboard"))


# LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "success")
    return redirect(url_for("login"))


# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)