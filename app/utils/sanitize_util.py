import bleach
import markdown
from markupsafe import Markup

# Tags and attributes allowed in rendered markdown output.
# No <script>, <style>, event handlers, or javascript: hrefs.
_ALLOWED_TAGS = [
    'p', 'br',
    'strong', 'em', 'b', 'i', 'u', 's', 'del',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'blockquote', 'code', 'pre',
    'a', 'hr',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]

_ALLOWED_ATTRS = {
    'a': ['href', 'title'],
}

# Only http/https/mailto — blocks javascript: and data: URIs
_ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_input(text: str) -> str:
    """Strip all HTML tags from raw user input before storing."""
    if not text:
        return ''
    return bleach.clean(text, tags=[], strip=True)


def render_markdown_safe(text: str) -> Markup:
    """Render markdown to HTML then whitelist-sanitize the output.
    Returns a Markup instance so Jinja2 does not double-escape it."""
    if not text:
        return Markup('')
    raw_html = markdown.markdown(
        text,
        extensions=['fenced_code', 'tables'],
    )
    clean_html = bleach.clean(
        raw_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        protocols=_ALLOWED_PROTOCOLS,
        strip=True,
    )
    return Markup(clean_html)
