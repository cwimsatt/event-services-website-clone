from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_ckeditor import CKEditor, CKEditorField
from app import app, db
from models import User, Category, Event, Testimonial, Contact

# Initialize CKEditor
ckeditor = CKEditor(app)

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_custom.login'))

class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('admin_custom.login'))
        return super().index()

class EventModelView(SecureModelView):
    column_list = ('title', 'category', 'date')
    column_searchable_list = ['title']
    column_filters = ['category_id', 'date']
    form_excluded_columns = ['image_path', 'video_path']
    form_overrides = {
        'description': CKEditorField
    }
    create_template = 'admin/event_create.html'
    edit_template = 'admin/event_edit.html'

class CategoryModelView(SecureModelView):
    column_list = ('name', 'slug')
    column_searchable_list = ['name']
    form_excluded_columns = ['events']

class TestimonialModelView(SecureModelView):
    column_list = ('client_name', 'event_type', 'date')
    column_searchable_list = ['client_name', 'event_type']
    form_overrides = {
        'content': CKEditorField
    }

class ContactModelView(SecureModelView):
    column_list = ('name', 'email', 'date')
    column_searchable_list = ['name', 'email']
    can_create = False

# Initialize Flask-Admin
admin = Admin(app, name='Event Services Admin', template_mode='bootstrap4', index_view=SecureAdminIndexView())

# Add model views
admin.add_view(CategoryModelView(Category, db.session))
admin.add_view(EventModelView(Event, db.session))
admin.add_view(TestimonialModelView(Testimonial, db.session))
admin.add_view(ContactModelView(Contact, db.session))
