from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_ckeditor import CKEditorField
from extensions import db
from models import User, Category, Event, Testimonial, Contact, Theme, ThemeColors, Theme, ThemeColors

def init_admin(app):
    """Initialize Flask-Admin with secure views."""
    try:
        admin = Admin(
            app,
            name='Event Services Admin',
            template_mode='bootstrap4',
            index_view=SecureAdminIndexView()
        )
        
        # Add model views with proper session management
        with app.app_context():
            admin.add_view(CategoryModelView(Category, db.session))
            admin.add_view(EventModelView(Event, db.session))
            admin.add_view(TestimonialModelView(Testimonial, db.session))
            admin.add_view(ContactModelView(Contact, db.session))
            admin.add_view(ThemeModelView(Theme, db.session))
        
        app.logger.info("Flask-Admin initialized successfully")
        return admin
    except Exception as e:
        app.logger.error(f"Error initializing admin: {str(e)}")
        raise

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

class ThemeModelView(SecureModelView):
    column_list = ('name', 'slug', 'is_custom', 'is_active')
    column_searchable_list = ['name']
    form_columns = ('name', 'slug', 'is_custom', 'is_active', 'colors')
    form_excluded_columns = None
    inline_models = [(ThemeColors, dict(
        form_columns=['primary_color', 'secondary_color', 'accent_color']
    ))]
    create_template = 'admin/theme_form.html'
    edit_template = 'admin/theme_form.html'

    def on_model_change(self, form, model, is_created):
        # Ensure only one theme is active at a time
        if model.is_active:
            Theme.query.filter(Theme.id != model.id).update({'is_active': False})
            db.session.commit()
        
        # Create default colors if none exist
        if not model.colors:
            colors = ThemeColors(
                theme=model,
                primary_color='#000000',
                secondary_color='#FFFFFF',
                accent_color='#808080'
            )
            db.session.add(colors)

# Admin initialization is now handled in app.py's register_extensions function