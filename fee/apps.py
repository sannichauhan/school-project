# fee/apps.py
from django.apps import AppConfig

class FeeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fee'

    def ready(self):
        import fee.signals  # Configuration verification connection setup load