from django.apps import AppConfig


class PlansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plans'

    def ready(self):
        """
        Register Celery tasks when Django app is ready.
        """
        import plans.tasks  # noqa
