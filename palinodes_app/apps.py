from django.apps import AppConfig


class PalinodesAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "palinodes_app"

    def ready(self) -> None:
        from . import signals