from django.apps import AppConfig


class IdealoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'idealo_app'
    def ready(self):
        import idealo_app.signals
