# Fobi REST API Usage Guide

## Getting Form Fields for Frontend Rendering

There are two ways to get form fields structure from the Fobi DRF integration:

### Method 1: OPTIONS Request (Default DRF Approach)

The OPTIONS method should return form metadata including the PUT request schema:

```bash
curl -X 'OPTIONS' \
  'http://localhost:8080/api/fobi-form-entry/test-form/' \
  -H 'accept: application/json'
```

**Expected Response:**
```json
{
  "name": "Fobi Form Entry Instance",
  "description": "FormEntry view set.",
  "renders": ["application/json", "text/html"],
  "parses": ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"],
  "actions": {
    "PUT": {
      // This should contain the form fields schema
      // but may be empty {} if dynamic serializer doesn't expose it properly
    }
  }
}
```

**Note:** The `actions.PUT` section should contain the form fields schema, but due to how fobi's dynamic serializers work, it might be empty. If it's empty, use Method 2.

### Method 2: Custom Form Fields Endpoint (Recommended)

A custom endpoint that explicitly returns form fields structure:

```bash
curl -X 'GET' \
  'http://localhost:8080/api/fobi-form-fields/test-form/' \
  -H 'accept: application/json'
```

**Response:**
```json
{
  "id": 3,
  "slug": "test-form",
  "title": "Test Form",
  "fields": [
    {
      "name": "full_name",
      "type": "CharField",
      "label": "Full Name",
      "required": true,
      "help_text": "",
      "max_length": 255
    },
    {
      "name": "email",
      "type": "EmailField",
      "label": "Email Address",
      "required": true,
      "help_text": ""
    },
    {
      "name": "age",
      "type": "IntegerField",
      "label": "Age",
      "required": false,
      "min_value": 0,
      "max_value": 120
    },
    {
      "name": "country",
      "type": "ChoiceField",
      "label": "Country",
      "required": false,
      "choices": [
        {"value": "USA", "label": "USA"},
        {"value": "Canada", "label": "Canada"},
        {"value": "Mexico", "label": "Mexico"}
      ]
    }
  ]
}
```

## Complete API Workflow

1. **List all forms:**
   ```bash
   GET /api/fobi-form-entry/
   ```

2. **Get form fields structure:**
   ```bash
   GET /api/fobi-form-fields/{slug}/
   # OR
   OPTIONS /api/fobi-form-entry/{slug}/
   ```

3. **Submit form data:**
   ```bash
   PUT /api/fobi-form-entry/{slug}/
   Content-Type: application/json
   
   {
     "full_name": "John Doe",
     "email": "john@example.com",
     "age": 30,
     "country": "USA"
   }
   ```

## Adding Test Form Submissions via REST API

To add 10 test form submissions for a form (e.g. form entry id 4) so you can check entries in admin:

1. Start the server: `python manage.py runserver 8080`
2. Run: `poetry run python manage.py add_rest_api_form_data --form-entry-id=4`

Options:
- `--form-entry-id=4` (default) – FormEntry PK from the admin edit URL
- `--count=10` (default) – number of submissions to send
- `--base-url=http://localhost:8080` – base URL of the running app

Submitted data is stored by the db_store handler only if the form has the **DB store** handler attached (in the form edit view: Form handlers section). View saved submissions in the Django admin at:

- **Saved form data entries:**  
  `http://localhost:8080/admin/fobi_contrib_plugins_form_handlers_db_store/savedformdataentry/`

(List and filter by form, user, created; export to CSV/XLS via actions.)

If the list is empty after submitting via API, ensure the form has the **DB store** handler: open the form in admin (e.g. edit form 4), go to the **Form handlers** section, and add the **DB store** handler if missing. You can also run `python manage.py attach_db_store_handler` to attach it to all forms that don’t have it.

## Field Types Mapping

The API returns field types that map to frontend form controls:

- `CharField` → Text input
- `EmailField` → Email input
- `IntegerField` → Number input
- `BooleanField` → Checkbox
- `ChoiceField` → Select dropdown
- `DateField` → Date picker
- `TextareaField` → Textarea

