from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, current_app

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512))  # Increased length to accommodate longer password hashes
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    sequence = db.Column(db.Float(precision=3), nullable=True)
    columns_per_row = db.Column(db.Integer, default=3, nullable=False)
    events = db.relationship('Event', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

import os
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'wmv'}  # Extended video formats
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename, allowed_extensions):
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(500))
    video_path = db.Column(db.String(500))
    sequence = db.Column(db.Float(precision=3), nullable=True)
    
    @property
    def image_url(self):
        if self.image_path and self.image_path.strip():
            # Ensure path is relative to static folder
            full_path = os.path.join(current_app.static_folder, self.image_path.lstrip('/'))
            if os.path.exists(full_path):
                return url_for('static', filename=self.image_path.lstrip('/'))
            current_app.logger.warning(f"Image not found at {full_path}")
        return url_for('static', filename='images/placeholder.svg')

    @staticmethod
    def validate_image(file):
        if not file:
            raise ValueError("No image file provided")
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            raise ValueError("Invalid image format. Allowed formats: jpg, jpeg, png")
        if file.content_length and file.content_length > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB")
        return True

    @staticmethod
    def validate_video(file):
        if not file:
            return True  # Video is optional
        if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            raise ValueError(f"Invalid video format. Allowed formats: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")
        if file.content_length and file.content_length > MAX_VIDEO_SIZE:
            raise ValueError(f"Video file size exceeds maximum limit of {MAX_VIDEO_SIZE // (1024*1024)}MB")
        return True

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    is_custom = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    colors = db.relationship('ThemeColors', backref='theme', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Theme {self.name}>'

class ThemeColors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)
    primary_color = db.Column(db.String(7), nullable=False)  # Hex color code (#RRGGBB)
    secondary_color = db.Column(db.String(7), nullable=False)
    accent_color = db.Column(db.String(7), nullable=False)

    def __repr__(self):
        return f'<ThemeColors for {self.theme.name}>'