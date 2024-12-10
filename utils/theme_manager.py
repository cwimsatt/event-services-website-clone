from flask import current_app, g
from models import Theme, ThemeColors

def get_active_theme():
    """Get the currently active theme."""
    if 'active_theme' not in g:
        g.active_theme = Theme.query.filter_by(is_active=True).first()
    return g.active_theme

def get_theme_colors():
    """Get colors for the active theme."""
    theme = get_active_theme()
    if theme and theme.colors:
        return {
            'primary': theme.colors.primary_color,
            'secondary': theme.colors.secondary_color,
            'accent': theme.colors.accent_color
        }
    return {
        'primary': '#000000',
        'secondary': '#FFFFFF',
        'accent': '#808080'
    }

def inject_theme():
    """Context processor to inject theme data into templates."""
    return dict(
        active_theme=get_active_theme(),
        theme_colors=get_theme_colors()
    )
