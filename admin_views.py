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
            current_app.logger.info(f"Processing theme changes for theme ID {model.id if not is_created else 'new'}")
            current_app.logger.info(f"Form data - is_active: {model.is_active}")
            
            # Store original is_active state before processing
            should_activate = model.is_active
            
            # Process colors first
            for color_field in ['primary_color', 'secondary_color', 'accent_color']:
                color_value = getattr(form, color_field).data
                current_app.logger.debug(f"Processing {color_field}: {color_value}")
                if color_value and not color_value.startswith('#'):
                    current_app.logger.error(f"Invalid color format for {color_field}: {color_value}")
                    raise ValueError(f"Invalid color format for {color_field}. Must start with '#'")
            
            try:
                if not model.colors:
                    current_app.logger.info("Creating new theme colors")
                    colors = ThemeColors(
                        theme=model,
                        primary_color=form.primary_color.data or '#f8f5f2',
                        secondary_color=form.secondary_color.data or '#2c3e50',
                        accent_color=form.accent_color.data or '#e67e22'
                    )
                    db.session.add(colors)
                else:
                    current_app.logger.info("Updating existing theme colors")
                    model.colors.primary_color = form.primary_color.data or model.colors.primary_color
                    model.colors.secondary_color = form.secondary_color.data or model.colors.secondary_color
                    model.colors.accent_color = form.accent_color.data or model.colors.accent_color

                # Save color changes
                db.session.flush()
                current_app.logger.info("Theme colors saved successfully")
                
            except Exception as color_error:
                current_app.logger.error(f"Error processing theme colors: {str(color_error)}")
                raise ValueError(f"Failed to save theme colors: {str(color_error)}")
            
            # Handle theme activation separately using direct SQL for atomicity
            if should_activate:
                current_app.logger.info(f"Processing theme activation request for theme ID {model.id}")
                
                try:
                    # Only proceed with activation if we have a valid ID
                    if not model.id:
                        current_app.logger.error("Cannot activate theme: No ID available")
                        raise ValueError("Cannot activate theme without a valid ID")

                    # Begin a transaction for theme activation
                    current_app.logger.info("Starting theme activation transaction")
                    
                    try:
                        # First verify the theme exists
                        verify_stmt = text("""
                            SELECT EXISTS(
                                SELECT 1 FROM theme WHERE id = :theme_id
                            )
                        """)
                        exists = db.session.execute(verify_stmt, {"theme_id": model.id}).scalar()
                        
                        if not exists:
                            current_app.logger.error(f"Theme {model.id} does not exist in database")
                            raise ValueError(f"Theme {model.id} not found")

                        # Deactivate all themes atomically
                        current_app.logger.info("Deactivating all themes")
                        db.session.execute(text("UPDATE theme SET is_active = FALSE"))
                        
                        # Activate the selected theme
                        current_app.logger.info(f"Activating theme {model.id}")
                        result = db.session.execute(
                            text("UPDATE theme SET is_active = TRUE WHERE id = :id"),
                            {"id": model.id}
                        )
                        
                        if result.rowcount != 1:
                            current_app.logger.error(f"Theme activation failed: Updated {result.rowcount} rows")
                            raise ValueError("Failed to activate theme")
                        
                        # Verify the final state
                        active_count = db.session.execute(
                            text("SELECT COUNT(*) FROM theme WHERE is_active = TRUE")
                        ).scalar()
                        
                        if active_count != 1:
                            current_app.logger.error(f"Invalid theme state: {active_count} active themes")
                            raise ValueError(f"Theme activation resulted in {active_count} active themes")
                        
                        # If we got here, everything worked
                        current_app.logger.info(f"Theme {model.id} activated successfully")
                        db.session.commit()
                        
                    except Exception as e:
                        current_app.logger.error(f"Error during theme activation SQL operations: {str(e)}")
                        db.session.rollback()
                        raise
                        
                    # Refresh the model to reflect the new state
                    db.session.refresh(model)
                    
                except Exception as e:
                    error_msg = f"Theme activation failed: {str(e)}"
                    current_app.logger.error(error_msg)
                    raise ValueError(error_msg)
            
            return model
            
        except Exception as e:
            current_app.logger.error(f"Error in theme processing: {str(e)}")
            db.session.rollback()
            raise ValueError(str(e))

# Admin initialization is now handled in app.py's register_extensions function