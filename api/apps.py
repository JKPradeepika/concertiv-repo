from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    icon_name = "home"

    def ready(self) -> None:
        from . import signals  # noqa: F401

        # for above: signals uses @receiver, so signal handlers are implicitly connected.
        # see https://docs.djangoproject.com/en/4.1/topics/signals/
