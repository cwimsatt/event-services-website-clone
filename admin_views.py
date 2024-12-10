from flask import redirect, url_for, current_app
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_ckeditor import CKEditorField
from wtforms import StringField
from sqlalchemy import text
from extensions import db
from models import User, Category, Event, Testimonial, Contact, Theme, ThemeColors

def init_admin(app):
    """Initialize Flask-Admin with secure views."""
    try:
        admin = Admin(
            app,
            name='Event Services Admin',
            template_mode='bootstrap4',
            base_template='admin/base.html',
            index_view=SecureAdminIndexView()
        )
        
        # Add model views with proper session management
        with app.app_context():
            try:
                admin.add_view(CategoryModelView(Category, db.session))
                admin.add_view(EventModelView(Event, db.session))
                admin.add_view(TestimonialModelView(Testimonial, db.session))
                admin.add_view(ContactModelView(Contact, db.session))
                admin.add_view(ThemeModelView(Theme, db.session))
                app.logger.info("All admin views initialized successfully")
            except Exception as view_error:
                app.logger.error(f"Error adding admin views: {str(view_error)}")
                raise
        
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
    column_list = ('name', 'is_custom', 'is_active')
    column_searchable_list = ['name']
    form_columns = ('name', 'is_custom', 'is_active')
    can_edit = True
    can_create = True
    can_delete = True
    edit_modal = False
    create_modal = False

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.primary_color = StringField('Primary Color')
        form_class.secondary_color = StringField('Secondary Color')
        form_class.accent_color = StringField('Accent Color')
        return form_class
    
    def on_form_prefill(self, form, id):
        """Pre-fill the form with existing theme colors"""
        theme = self.get_one(id)
        if theme and theme.colors:
            form.primary_color.data = theme.colors.primary_color
            form.secondary_color.data = theme.colors.secondary_color
            form.accent_color.data = theme.colors.accent_color
    
    def create_form(self):
        form = super().create_form()
        # Initialize with default theme colors
        return form
        
    def edit_form(self, obj):
        form = super().edit_form(obj)
        return form
    
    def on_model_change(self, form, model, is_created):
        """Handle theme changes with proper validation and error handling."""
        try:
            # Store original is_active state before processing
            should_activate = model.is_active
            
            # Process colors first
            for color_field in ['primary_color', 'secondary_color', 'accent_color']:
                color_value = getattr(form, color_field).data
                if color_value and not color_value.startswith('#'):
                    raise ValueError(f"Invalid color format for {color_field}. Must start with '#'")
            
            if not model.colors:
                colors = ThemeColors(
                    theme=model,
                    primary_color=form.primary_color.data or '#f8f5f2',
                    secondary_color=form.secondary_color.data or '#2c3e50',
                    accent_color=form.accent_color.data or '#e67e22'
                )
                db.session.add(colors)
            else:
                model.colors.primary_color = form.primary_color.data or model.colors.primary_color
                model.colors.secondary_color = form.secondary_color.data or model.colors.secondary_color
                model.colors.accent_color = form.accent_color.data or model.colors.accent_color

            # Save changes before handling activation
            db.session.flush()
            
            # Handle theme activation separately using direct SQL for atomicity
            if should_activate:
                try:
                    current_app.logger.info(f"Starting theme activation for theme ID {model.id}")
                    
                    # First verify the theme exists
                    verify_theme_stmt = text("SELECT id FROM theme WHERE id = :theme_id")
                    theme_exists = db.session.execute(verify_theme_stmt, {"theme_id": model.id}).scalar()
                    
                    if not theme_exists:
                        current_app.logger.error(f"Theme with ID {model.id} not found")
                        raise ValueError(f"Theme with ID {model.id} does not exist")
                    
                    # Deactivate all themes first
                    current_app.logger.info("Deactivating all themes")
                    deactivate_stmt = text("UPDATE theme SET is_active = FALSE")
                    db.session.execute(deactivate_stmt)
                    
                    # Then activate the selected theme
                    current_app.logger.info(f"Activating theme {model.id}")
                    activate_stmt = text("UPDATE theme SET is_active = TRUE WHERE id = :theme_id")
                    db.session.execute(activate_stmt, {"theme_id": model.id})
                    
                    # Commit the changes
                    db.session.commit()
                    current_app.logger.info(f"Theme activation completed for ID {model.id}")
                    
                    # Verify the changes
                    verify_stmt = text("SELECT COUNT(*) FROM theme WHERE is_active = TRUE")
                    active_count = db.session.execute(verify_stmt).scalar()
                    current_app.logger.info(f"Active themes after update: {active_count}")
                    
                    if active_count != 1:
                        current_app.logger.error(f"Inconsistent theme state: {active_count} active themes")
                        raise ValueError(f"Theme activation failed: {active_count} active themes found")
                    
                    # Refresh the model to get the updated state
                    db.session.refresh(model)
                    
                except Exception as e:
                    current_app.logger.error(f"Error during theme activation: {str(e)}")
                    db.session.rollback()
                    raise ValueError(f"Failed to activate theme: {str(e)}")
            
            return model
            
        except Exception as e:
            current_app.logger.error(f"Error in theme processing: {str(e)}")
            db.session.rollback()
            raise ValueError(str(e))

# Admin initialization is now handled in app.py's register_extensions function