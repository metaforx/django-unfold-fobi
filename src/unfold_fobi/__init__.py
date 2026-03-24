"""unfold_fobi package initialization."""

import warnings

__version__ = "0.1.2"

# Python 3.12 emits SyntaxWarning for invalid escape sequences in older fobi
# releases (fobi.base uses "\s" in non-raw strings). Suppress only this known
# third-party warning to keep startup output clean.
warnings.filterwarnings(
    "ignore",
    message=r"invalid escape sequence '\\\\s'",
    category=SyntaxWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r"invalid escape sequence '\\s'",
    category=SyntaxWarning,
)
