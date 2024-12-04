import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
app = Flask(__name__)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

login_manager.init_app(app)
login_manager.login_view = 'admin.login'
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///events.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

with app.app_context():
    import models
    import routes
    from admin_routes import admin
    app.register_blueprint(admin)
    db.create_all()
    
    # Create admin user if it doesn't exist
    from models import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@example.com', is_admin=True)
        admin_user.set_password('admin')  # Default password, should be changed
        db.session.add(admin_user)
        db.session.commit()
