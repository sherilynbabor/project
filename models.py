from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------- USER MODEL ----------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # RELATIONSHIP
    crops = db.relationship(
        "Crop",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # ---------------- SECURITY HELPERS ----------------
    def set_password(self, password):
        """Hash password before saving"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------- CROP MODEL ----------------
class Crop(db.Model):
    __tablename__ = "crops"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    # Controlled values (safer than free text)
    status = db.Column(
        db.String(50),
        default="Growing",
        nullable=False
    )

    notes = db.Column(db.Text)

    # store filename only (recommended)
    image = db.Column(db.String(255))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # INDEXED FK (better performance)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ---------------- OPTIONAL HELPER ----------------
    def to_dict(self):
        """Useful for APIs / frontend integration"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "notes": self.notes,
            "image": self.image,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id
        }

    def __repr__(self):
        return f"<Crop {self.name}>"