from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)  # Vérifie si un user avec cet email existe
        except User.DoesNotExist:
            return None

        if user.check_password(password):  # Vérifie le mot de passe
            return user
        return None