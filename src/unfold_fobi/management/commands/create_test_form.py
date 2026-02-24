"""
Management command to create a test form with basic fields for testing Fobi DRF integration.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from fobi.models import FormEntry, FormElementEntry, FormHandlerEntry

User = get_user_model()
from fobi.contrib.apps.drf_integration.form_elements.fields.text.base import TextInputPlugin
from fobi.contrib.apps.drf_integration.form_elements.fields.email.base import EmailInputPlugin
from fobi.contrib.apps.drf_integration.form_elements.fields.integer.base import IntegerInputPlugin
from fobi.contrib.apps.drf_integration.form_elements.fields.boolean.base import BooleanSelectPlugin
from fobi.contrib.apps.drf_integration.form_elements.fields.textarea.base import TextareaPlugin
from fobi.contrib.apps.drf_integration.form_elements.fields.date.base import DateSelectPlugin
from fobi.contrib.apps.drf_integration.form_elements.fields.select.base import SelectInputPlugin


class Command(BaseCommand):
    help = 'Create a test form with basic fields for testing Fobi DRF integration'

    def handle(self, *args, **options):
        # Get or create a user for the form
        user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if not user:
            # Try to get the first superuser
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('No user found. Please create a superuser first.'))
                return

        # Check if form already exists
        form_slug = 'test-form'
        form_entry, created = FormEntry.objects.get_or_create(
            slug=form_slug,
            defaults={
                'name': 'Test Form',
                'user': user,
                'is_public': True,
                'is_cloneable': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created form: {form_entry.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Form "{form_entry.name}" already exists. Updating...'))
            # Clear existing form elements
            FormElementEntry.objects.filter(form_entry=form_entry).delete()

        # Ensure DB store handler is attached so REST API submissions are saved
        FormHandlerEntry.objects.get_or_create(
            form_entry=form_entry,
            plugin_uid='db_store',
            defaults={'position': 0},
        )

        # Create form fields
        fields_data = [
            {
                'plugin': TextInputPlugin,
                'position': 1,
                'data': {
                    'label': 'Full Name',
                    'name': 'full_name',
                    'required': True,
                    'placeholder': 'Enter your full name',
                    'initial': '',
                }
            },
            {
                'plugin': EmailInputPlugin,
                'position': 2,
                'data': {
                    'label': 'Email Address',
                    'name': 'email',
                    'required': True,
                    'placeholder': 'Enter your email address',
                    'initial': '',
                }
            },
            {
                'plugin': IntegerInputPlugin,
                'position': 3,
                'data': {
                    'label': 'Age',
                    'name': 'age',
                    'required': False,
                    'placeholder': 'Enter your age',
                    'initial': '',
                    'min_value': 0,
                    'max_value': 120,
                }
            },
            {
                'plugin': TextareaPlugin,
                'position': 4,
                'data': {
                    'label': 'Message',
                    'name': 'message',
                    'required': False,
                    'placeholder': 'Enter your message',
                    'initial': '',
                    'rows': 5,
                }
            },
            {
                'plugin': BooleanSelectPlugin,
                'position': 5,
                'data': {
                    'label': 'Subscribe to Newsletter',
                    'name': 'subscribe',
                    'required': False,
                    'initial': False,
                }
            },
            {
                'plugin': DateSelectPlugin,
                'position': 6,
                'data': {
                    'label': 'Date of Birth',
                    'name': 'date_of_birth',
                    'required': False,
                    'initial': '',
                }
            },
            {
                'plugin': SelectInputPlugin,
                'position': 7,
                'data': {
                    'label': 'Country',
                    'name': 'country',
                    'required': False,
                    'initial': '',
                    'choices': 'USA,Canada,Mexico,UK,Germany,France,Other',
                }
            },
        ]

        for field_data in fields_data:
            # Create the form element entry
            element_entry = FormElementEntry(
                form_entry=form_entry,
                plugin_uid=field_data['plugin'].uid,
                position=field_data['position'],
            )
            # Set the form data directly (stored as JSON)
            element_entry.form_data = field_data['data']
            element_entry.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'  Added field: {field_data["data"]["label"]} ({field_data["plugin"].name})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created/updated test form with {len(fields_data)} fields!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Form slug: {form_slug}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'API endpoint: /api/fobi-form-entry/{form_slug}/'
            )
        )

