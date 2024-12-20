from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
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
    """Get colors for the active theme with real-time updates."""
    try:
        # Force a fresh database query to get the latest theme colors
        db.session.expire_all()
        active_theme = get_active_theme()
        
        if active_theme and active_theme.colors:
            theme_colors = {
                'primary': active_theme.colors.primary_color,
                'secondary': active_theme.colors.secondary_color,
                'accent': active_theme.colors.accent_color
            }
            current_app.logger.info(f"Retrieved theme colors for {active_theme.name}: {theme_colors}")
            return theme_colors
            
        current_app.logger.warning("No active theme found, check database")
        raise ValueError("No active theme found")
    except Exception as e:
        current_app.logger.error(f"Error getting theme colors: {str(e)}")
        raise

def inject_theme():
    """Context processor to inject theme data into templates with real-time updates."""
    try:
        # Clear any cached theme data
        db.session.expire_all()
        
        # Get active theme and colors
        active_theme = get_active_theme()
        if not active_theme:
            current_app.logger.error("No active theme found in database")
            raise ValueError("No active theme found")
            
        # Get theme colors
        if not active_theme.colors:
            current_app.logger.error(f"No colors found for active theme {active_theme.name}")
            raise ValueError(f"No colors found for theme {active_theme.name}")
            
        # Log the actual color values
        current_app.logger.info(f"""
            Injecting theme colors for {active_theme.name}:
            Primary: {active_theme.colors.primary_color}
            Secondary: {active_theme.colors.secondary_color}
            Accent: {active_theme.colors.accent_color}
        """)
        
        colors = {
            'primary': active_theme.colors.primary_color,
            'secondary': active_theme.colors.secondary_color,
            'accent': active_theme.colors.accent_color
        }
        
        return {
            'active_theme': active_theme,
            'theme_colors': colors,
            'theme_updated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        current_app.logger.error(f"Critical error in theme injection: {str(e)}")
        raise  # Let the error propagate so we can see it in the logs

def initialize_default_themes():
    """Initialize default themes if none exist."""
    from models import Theme, ThemeColors
    
    try:
        # Check if any themes exist
        if Theme.query.count() > 0:
            current_app.logger.info("Themes already exist, skipping initialization")
            # Ensure at least one theme is active
            if not Theme.query.filter_by(is_active=True).first():
                try:
                    first_theme = Theme.query.first()
                    current_app.logger.info(f"Setting first theme {first_theme.id} as active")
                    # Use the same SQL pattern as admin views
                    db.session.execute(text("UPDATE theme SET is_active = FALSE"))
                    db.session.execute(
                        text("UPDATE theme SET is_active = TRUE WHERE id = :theme_id"),
                        {"theme_id": first_theme.id}
                    )
                    db.session.commit()
                    current_app.logger.info(f"Successfully activated theme: {first_theme.name}")
                except Exception as e:
                    current_app.logger.error(f"Error activating initial theme: {str(e)}")
                    db.session.rollback()
                    raise
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
