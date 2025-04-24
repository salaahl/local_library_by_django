from django.conf import settings

def custom_settings(request):
    return {
        'APP_NAME': settings.APP_NAME
    }
