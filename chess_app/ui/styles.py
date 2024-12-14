# chess_app/ui/styles.py

class Styles:
    """
    Styles class to define color schemes and font settings for the Tkinter UI.
    Supports light and dark modes.
    """

    LIGHT_THEME = {
        "background": "#F5F5F5",
        "foreground": "#000000",
        "button_bg": "#E0E0E0",
        "button_fg": "#000000",
        "highlight_color": "#0073e6",
        "chessboard_light": "#f0d9b5",
        "chessboard_dark": "#b58863",
        "status_success": "#00a651",
        "status_error": "#d9534f",
        "status_info": "#5bc0de",
    }

    DARK_THEME = {
        "background": "#2E2E2E",
        "foreground": "#FFFFFF",
        "button_bg": "#4D4D4D",
        "button_fg": "#FFFFFF",
        "highlight_color": "#1E90FF",
        "chessboard_light": "#CCCCCC",
        "chessboard_dark": "#333333",
        "status_success": "#28a745",
        "status_error": "#dc3545",
        "status_info": "#17a2b8",
    }

    CURRENT_THEME = LIGHT_THEME

    @classmethod
    def toggle_theme(cls):
        if cls.CURRENT_THEME == cls.LIGHT_THEME:
            cls.CURRENT_THEME = cls.DARK_THEME
        else:
            cls.CURRENT_THEME = cls.LIGHT_THEME