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
            current_app.logger.info(f"Processing theme change for theme: {model.name} (id: {model.id})")
            
            # Store the original is_active state
            original_is_active = model.is_active
            
            # Process theme activation separately from other changes
            if original_is_active:
                current_app.logger.info(f"Activating theme: {model.name}")
                try:
                    # Use explicit transaction for theme activation
                    with db.session.begin_nested():
                        # First deactivate all themes
                        db.session.execute(text("UPDATE theme SET is_active = false"))
                        # Then activate only the current theme
                        db.session.execute(
                            text("UPDATE theme SET is_active = true WHERE id = :id"),
                            {"id": model.id}
                        )
                        db.session.flush()
                except Exception as e:
                    current_app.logger.error(f"Error in theme activation transaction: {str(e)}")
                    raise
            else:
                # Check if this is the last active theme
                active_themes = Theme.query.filter(Theme.is_active == True).count()
                current_app.logger.debug(f"Active themes count: {active_themes}")
                if active_themes <= 1 and not is_created and Theme.query.get(model.id).is_active:
                    raise ValueError("Cannot deactivate the last active theme")
                    
                # If we're deactivating a theme, make sure we still have at least one active theme
                if not is_created and Theme.query.get(model.id).is_active:
                    active_count = Theme.query.filter(Theme.is_active == True).count()
                    if active_count <= 1:
                        raise ValueError("Cannot deactivate the last active theme")
                
                # Process theme colors
                try:
                    # Validate color format
                    for color_field in ['primary_color', 'secondary_color', 'accent_color']:
                        color_value = getattr(form, color_field).data
                        if color_value and not color_value.startswith('#'):
                            raise ValueError(f"Invalid color format for {color_field}. Must start with '#'")
                    
                    # Update or create theme colors
                    if not model.colors:
                        current_app.logger.info(f"Creating new colors for theme: {model.name}")
                        colors = ThemeColors(
                            theme=model,
                            primary_color=form.primary_color.data or '#f8f5f2',
                            secondary_color=form.secondary_color.data or '#2c3e50',
                            accent_color=form.accent_color.data or '#e67e22'
                        )
                        db.session.add(colors)
                    else:
                        current_app.logger.info(f"Updating colors for theme: {model.name}")
                        model.colors.primary_color = form.primary_color.data or model.colors.primary_color
                        model.colors.secondary_color = form.secondary_color.data or model.colors.secondary_color
                        model.colors.accent_color = form.accent_color.data or model.colors.accent_color
                except Exception as color_error:
                    current_app.logger.error(f"Error processing theme colors: {str(color_error)}")
                    raise ValueError(f"Error processing theme colors: {str(color_error)}")

            current_app.logger.info(f"Theme {model.name} processed successfully")
            return model
            
        except ValueError as e:
            current_app.logger.error(f"Theme activation error: {str(e)}")
            db.session.rollback()
            raise ValueError(str(e))
        except Exception as e:
            current_app.logger.error(f"Unexpected error in theme activation: {str(e)}")
            db.session.rollback()
            raise

# Admin initialization is now handled in app.py's register_extensions function