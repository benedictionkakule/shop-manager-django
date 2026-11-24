import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q

logger = logging.getLogger(__name__)


def _send(subject, body, recipients):
    """Send an email, but never let a mail problem break the shop."""
    if not recipients:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
    except Exception:
        logger.exception("Could not send email: %s", subject)


def _manager_emails():
    User = get_user_model()
    users = (
        User.objects.filter(is_active=True)
        .exclude(email="")
        .filter(Q(is_superuser=True) | Q(groups__name="Manager"))
        .distinct()
    )
    return [u.email for u in users]


def notify_sale(sale):
    """Email a receipt to the customer and low-stock alerts to the managers."""
    items = list(sale.items.select_related("product"))

    # 1. Receipt for the customer
    customer = sale.customer
    if customer and customer.email:
        lines = "\n".join(
            f"  {i.quantity} x {i.product.name} @ {i.unit_price} = {i.line_total}"
            for i in items
        )
        body = (
            f"Hello {customer.name},\n\n"
            f"Thank you for your purchase. Here is your receipt for sale #{sale.pk} "
            f"({sale.date:%Y-%m-%d %H:%M}):\n\n{lines}\n\n"
            f"Total: {sale.total}\n\nShop Manager"
        )
        _send(f"Your receipt - sale #{sale.pk}", body, [customer.email])

    # 2. Alert for products this sale pushed down to their reorder level
    sold = {}
    for item in items:
        sold[item.product] = sold.get(item.product, 0) + item.quantity
    low = [p for p, qty in sold.items() if p.quantity <= p.reorder_level < p.quantity + qty]

    if low:
        lines = "\n".join(
            f"  {p.name} ({p.sku}): {p.quantity} left, reorder level {p.reorder_level}"
            for p in low
        )
        _send(
            "Low stock alert",
            f"These products are running low after sale #{sale.pk}:\n\n{lines}\n\nPlease restock soon.",
            _manager_emails(),
        )
