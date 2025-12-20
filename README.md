# unfold-fobi

Django Unfold admin integration for django-fobi form builder.

## Description

`unfold-fobi` provides seamless integration between Django Unfold admin interface and django-fobi form builder, automatically applying Unfold widgets to all fobi forms for a consistent admin experience.

## Features

- Automatic widget application to fobi forms
- Unfold theme integration for fobi form builder
- Support for all standard Django form fields
- Compatible with Django 5.0+

## Installation

```bash
pip install unfold-fobi
```

## Requirements

- Python >= 3.10
- Django >= 5.0
- django-unfold
- django-fobi
- django-crispy-forms

## Usage

1. Add `unfold_fobi` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'unfold',
    'fobi',
    'fobi.contrib.themes.simple',
    'unfold_fobi',
    # ... rest of apps
]
```

2. The integration will automatically apply Unfold widgets to all fobi forms.

## Development

```bash
# Install in development mode
make install

# Run tests
make test

# Lint code
make lint
```

## License

MIT License

