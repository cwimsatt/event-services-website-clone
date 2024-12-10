from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from models import Theme, ThemeColors

def get_active_theme():
    """Get the currently active theme."""
    from models import Theme
    try:
        active_theme = Theme.query.filter_by(is_active=True).first()
        if active_theme:
            current_app.logger.debug(f"Retrieved active theme: {active_theme.name}")
            return active_theme
        current_app.logger.warning("No active theme found, using default")
        return None
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error getting active theme: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Unexpected error getting active theme: {str(e)}")
        return None

def get_theme_colors():
    """Get colors for the active theme."""
    active_theme = get_active_theme()
    if active_theme and active_theme.colors:
        return {
            'primary': active_theme.colors.primary_color,
            'secondary': active_theme.colors.secondary_color,
            'accent': active_theme.colors.accent_color
        }
    return {
        'primary': '#ffffff',
        'secondary': '#333333',
        'accent': '#007bff'
    }

def inject_theme():
    """Context processor to inject theme data into templates."""
    try:
        active_theme = get_active_theme()
        colors = get_theme_colors()
        current_app.logger.debug(f"Injecting theme data: active_theme={active_theme}, colors={colors}")
        return dict(
            active_theme=active_theme,
            theme_colors=colors
        )
    except Exception as e:
        current_app.logger.error(f"Error injecting theme data: {str(e)}")
        return dict(
            active_theme=None,
            theme_colors={
                'primary': '#ffffff',
                'secondary': '#333333',
                'accent': '#007bff'
            }
        )

def initialize_default_themes():
    """Initialize default themes if none exist."""
    from models import Theme, ThemeColors
    
    try:
        # Check if any themes exist
        if Theme.query.count() > 0:
            current_app.logger.info("Themes already exist, skipping initialization")
            # Ensure at least one theme is active
            if not Theme.query.filter_by(is_active=True).first():
                first_theme = Theme.query.first()
                first_theme.is_active = True
                db.session.commit()
                current_app.logger.info(f"Activated theme: {first_theme.name}")
            return

        current_app.logger.info("Initializing default themes")
        
        # Create default light theme
        light_theme = Theme(
            name="Light Theme",
            slug="light",
            is_custom=False,
            is_active=True
        )
        light_colors = ThemeColors(
            theme=light_theme,
            primary_color="#ffffff",
            secondary_color="#333333",
            accent_color="#007bff"
        )
        db.session.add(light_theme)
        current_app.logger.info("Added light theme")
        
        # Create default dark theme
        dark_theme = Theme(
            name="Dark Theme",
            slug="dark",
            is_custom=False,
            is_active=False
        )
        dark_colors = ThemeColors(
            theme=dark_theme,
            primary_color="#333333",
            secondary_color="#ffffff",
            accent_color="#17a2b8"
        )
        db.session.add(dark_theme)
        current_app.logger.info("Added dark theme")

        db.session.commit()
        current_app.logger.info("Default themes initialized successfully")
        
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error initializing themes: {str(e)}")
        db.session.rollback()
    except Exception as e:
        current_app.logger.error(f"Unexpected error initializing themes: {str(e)}")
        db.session.rollback()