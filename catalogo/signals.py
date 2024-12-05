from django.db.models.signals import post_migrate
from django.dispatch import receiver
from catalogo.models import Usuario

@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if not Usuario.objects.filter(email='admin@miempresa.com').exists():
        Usuario.objects.create_superuser(
            email='admin@miempresa.com',
            password='admin123',
            nombre='Admin'
        )
        print("Superuser 'admin@miempresa.com' created.")
