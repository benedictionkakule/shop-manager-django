import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from inventory.models import Category, Customer, Product, Sale, SaleItem, Supplier

# name, sku, category, supplier, price, stock, reorder level
CATALOGUE = [
    ("Mineral Water 1.5L", "DRK-001", "Drinks", "FreshFlow Distributors", 1500, 120, 20),
    ("Orange Juice 1L", "DRK-002", "Drinks", "FreshFlow Distributors", 4500, 40, 10),
    ("Soda 500ml", "DRK-003", "Drinks", "FreshFlow Distributors", 2000, 80, 15),
    ("Rice 5kg", "GRO-001", "Groceries", "Kampala Wholesale Ltd", 22000, 30, 8),
    ("Sugar 1kg", "GRO-002", "Groceries", "Kampala Wholesale Ltd", 5000, 45, 10),
    ("Cooking Oil 1L", "GRO-003", "Groceries", "Kampala Wholesale Ltd", 9500, 25, 10),
    ("Wheat Flour 2kg", "GRO-004", "Groceries", "Kampala Wholesale Ltd", 8000, 35, 10),
    ("Bar Soap", "HOU-001", "Household", "HomeCare Supplies", 3000, 60, 15),
    ("Laundry Detergent 1kg", "HOU-002", "Household", "HomeCare Supplies", 12000, 20, 6),
    ("Toilet Paper 4-pack", "HOU-003", "Household", "HomeCare Supplies", 6500, 28, 8),
    ("Biscuits Pack", "SNK-001", "Snacks", "Kampala Wholesale Ltd", 2500, 70, 15),
    ("Potato Crisps", "SNK-002", "Snacks", "FreshFlow Distributors", 3000, 50, 12),
]


class Command(BaseCommand):
    help = "Fill the database with demo data for the shop."

    def handle(self, *args, **options):
        random.seed(7)

        cats = {}
        for name in ("Drinks", "Groceries", "Household", "Snacks"):
            cats[name], _ = Category.objects.get_or_create(name=name)

        sups = {}
        for name, phone in (
            ("FreshFlow Distributors", "0700 100 200"),
            ("Kampala Wholesale Ltd", "0700 300 400"),
            ("HomeCare Supplies", "0700 500 600"),
        ):
            sups[name], _ = Supplier.objects.get_or_create(name=name, defaults={"phone": phone})

        for name, sku, cat, sup, price, stock, reorder in CATALOGUE:
            Product.objects.get_or_create(sku=sku, defaults={
                "name": name, "category": cats[cat], "supplier": sups[sup],
                "price": price, "quantity": stock, "reorder_level": reorder,
            })

        customers = [
            Customer.objects.get_or_create(name=n, defaults={"phone": p})[0]
            for n, p in (("Grace Namukasa", "0771 111 222"),
                         ("Peter Okello", "0772 333 444"),
                         ("Sarah Nakato", "0773 555 666"))
        ]

        if Sale.objects.count() >= 10:
            self.stdout.write("Sales already exist - skipping demo sales.")
            return

        user = get_user_model().objects.first()
        products = list(Product.objects.filter(sku__in=[row[1] for row in CATALOGUE]))

        for _ in range(25):
            sale = Sale.objects.create(
                customer=random.choice(customers + [None]), served_by=user
            )
            for product in random.sample(products, k=random.randint(1, 3)):
                product.refresh_from_db()
                qty = min(random.randint(1, 4), product.quantity)
                if qty < 1:
                    continue
                SaleItem.objects.create(
                    sale=sale, product=product, quantity=qty, unit_price=product.price
                )
                product.quantity -= qty
                product.save(update_fields=["quantity", "updated_at"])

            if not sale.items.exists():
                sale.delete()
                continue

            # Spread the sales over the last 7 days
            when = timezone.now() - timedelta(
                days=random.randint(0, 6), hours=random.randint(0, 8)
            )
            Sale.objects.filter(pk=sale.pk).update(date=when)

        # Make two products low on stock so the alerts show up
        Product.objects.filter(sku="GRO-003").update(quantity=4)
        Product.objects.filter(sku="HOU-002").update(quantity=2)

        self.stdout.write(self.style.SUCCESS("Demo data created."))
