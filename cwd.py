from app import app
from models import User
from extensions import db
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--pwd', required=True, help='New password for admin')
args = parser.parse_args()

# Then in your set_password call:

def update_admin_password():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found")
            return

        admin.set_password(args.pwd)
        db.session.commit()
        print("Admin password updated successfully")

if __name__ == '__main__':
    update_admin_password()
