from django.core.management import BaseCommand

from users.models import User
import os


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = os.getenv("SUPERUSER_EMAIL")
        password = os.getenv("SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write(
                self.style.ERROR('SUPERUSER_EMAIL or SUPERUSER_PASSWORD not set in environment variables.'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Superuser with email {email} already exists."))
        else:
            user = User.objects.create(email=email)
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} created successfully."))
