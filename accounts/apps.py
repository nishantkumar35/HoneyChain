from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Accounts & Profiles'

    def ready(self):
        # Import signals so BeekeeperProfile is auto-created on user save
        import accounts.signals  # noqa: F401

