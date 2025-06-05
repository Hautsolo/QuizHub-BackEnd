from django.apps import AppConfig

class QuizhubApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quizhubapi'
    
    def ready(self):
        import quizhubapi.signals