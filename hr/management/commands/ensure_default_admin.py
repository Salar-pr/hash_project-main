from django.core.management.base import BaseCommand

from hr.models import HRUser


class Command(BaseCommand):
    help = "Create/update the default Salar admin account."

    def handle(self, *args, **options):
        user, created = HRUser.objects.get_or_create(username="salar")
        user.set_password("12345678")
        user.role = HRUser.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.approve(None)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Default admin {'created' if created else 'updated'}: salar / 12345678"))
