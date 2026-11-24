from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

CASHIER_PERMISSIONS = [
    "view_category", "view_supplier", "view_product", "view_customer",
    "view_sale", "add_sale", "add_customer",
]


class Command(BaseCommand):
    help = "Create the Manager and Cashier groups with their permissions."

    def handle(self, *args, **options):
        inventory_perms = Permission.objects.filter(content_type__app_label="inventory")

        manager, _ = Group.objects.get_or_create(name="Manager")
        manager.permissions.set(inventory_perms)

        cashier, _ = Group.objects.get_or_create(name="Cashier")
        cashier.permissions.set(inventory_perms.filter(codename__in=CASHIER_PERMISSIONS))

        self.stdout.write(self.style.SUCCESS("Roles ready: Manager and Cashier."))
