import csv
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Product, Sale, SaleItem

# quantity x unit_price, calculated by the database
LINE_TOTAL = ExpressionWrapper(
    F("quantity") * F("unit_price"),
    output_field=DecimalField(max_digits=14, decimal_places=2),
)


def revenue(items):
    return items.aggregate(total=Sum(LINE_TOTAL))["total"] or Decimal("0")


def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=6)

    low_stock = (
        Product.objects.filter(quantity__lte=F("reorder_level"))
        .select_related("category")
        .order_by("quantity")
    )

    top_products = (
        SaleItem.objects.filter(sale__date__date__gte=month_start)
        .values("product__name")
        .annotate(sold=Sum("quantity"))
        .order_by("-sold")[:5]
    )

    # Revenue per day for the last 7 days (days with no sales count as 0)
    daily = {
        row["day"]: row["total"]
        for row in SaleItem.objects.filter(sale__date__date__gte=week_start)
        .annotate(day=TruncDate("sale__date"))
        .values("day")
        .annotate(total=Sum(LINE_TOTAL))
    }
    labels, values = [], []
    for i in range(7):
        d = week_start + timedelta(days=i)
        labels.append(d.strftime("%a %d"))
        values.append(float(daily.get(d, 0)))

    context = {
        "product_count": Product.objects.count(),
        "low_stock_count": low_stock.count(),
        "low_stock": low_stock[:8],
        "today_sales_count": Sale.objects.filter(date__date=today).count(),
        "today_revenue": revenue(SaleItem.objects.filter(sale__date__date=today)),
        "month_revenue": revenue(SaleItem.objects.filter(sale__date__date__gte=month_start)),
        "top_products": top_products,
        "recent_sales": Sale.objects.select_related("customer", "served_by")
        .prefetch_related("items")[:5],
        "chart_data": {"labels": labels, "values": values},
    }
    return render(request, "inventory/dashboard.html", context)


def _parse_date(value, default):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


def sales_report(request):
    today = timezone.localdate()
    start = _parse_date(request.GET.get("start"), today.replace(day=1))
    end = _parse_date(request.GET.get("end"), today)

    items = SaleItem.objects.filter(
        sale__date__date__gte=start, sale__date__date__lte=end
    )
    rows = list(
        items.values("product__name", "product__sku")
        .annotate(qty=Sum("quantity"), revenue=Sum(LINE_TOTAL))
        .order_by("-revenue")
    )
    total_qty = sum(r["qty"] for r in rows)
    total_revenue = sum((r["revenue"] for r in rows), Decimal("0"))
    sales_count = Sale.objects.filter(
        date__date__gte=start, date__date__lte=end
    ).count()

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="sales_{start}_{end}.csv"'
        writer = csv.writer(response)
        writer.writerow(["Product", "SKU", "Quantity sold", "Revenue"])
        for r in rows:
            writer.writerow([r["product__name"], r["product__sku"], r["qty"], r["revenue"]])
        writer.writerow([])
        writer.writerow(["Total", "", total_qty, total_revenue])
        return response

    return render(request, "inventory/sales_report.html", {
        "rows": rows, "start": start, "end": end,
        "total_qty": total_qty, "total_revenue": total_revenue,
        "sales_count": sales_count,
    })
