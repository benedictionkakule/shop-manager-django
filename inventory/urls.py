from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required, permission_required
from django.urls import path
from django.views.generic import RedirectView

from . import accounts, admin_tools, reports, views


def perm(codename, view):
    """Only users holding this permission may open the view (others get a 403 page)."""
    return permission_required(f"inventory.{codename}", raise_exception=True)(view)


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),

    # Authentication
    path("login/", login_not_required(auth_views.LoginView.as_view(
        template_name="registration/login.html",
        redirect_authenticated_user=True,
    )), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", accounts.signup, name="signup"),
    path("favicon.ico", login_not_required(RedirectView.as_view(url="/static/favicon.ico")), name="favicon"),

    # Dashboard, reports, admin tools
    path("dashboard/", reports.dashboard, name="dashboard"),
    path("reports/sales/", perm("view_reports", reports.sales_report), name="sales_report"),
    path("admin-tools/clear-recent-actions/", admin_tools.clear_recent_actions, name="clear_recent_actions"),

    # Products
    path("products/", perm("view_product", views.ProductListView.as_view()), name="product_list"),
    path("products/add/", perm("add_product", views.ProductCreateView.as_view()), name="product_create"),
    path("products/<int:pk>/", perm("view_product", views.ProductDetailView.as_view()), name="product_detail"),
    path("products/<int:pk>/edit/", perm("change_product", views.ProductUpdateView.as_view()), name="product_update"),
    path("products/<int:pk>/delete/", perm("delete_product", views.ProductDeleteView.as_view()), name="product_delete"),

    # Categories
    path("categories/", perm("view_category", views.CategoryListView.as_view()), name="category_list"),
    path("categories/add/", perm("add_category", views.CategoryCreateView.as_view()), name="category_create"),
    path("categories/<int:pk>/edit/", perm("change_category", views.CategoryUpdateView.as_view()), name="category_update"),
    path("categories/<int:pk>/delete/", perm("delete_category", views.CategoryDeleteView.as_view()), name="category_delete"),

    # Suppliers
    path("suppliers/", perm("view_supplier", views.SupplierListView.as_view()), name="supplier_list"),
    path("suppliers/add/", perm("add_supplier", views.SupplierCreateView.as_view()), name="supplier_create"),
    path("suppliers/<int:pk>/edit/", perm("change_supplier", views.SupplierUpdateView.as_view()), name="supplier_update"),
    path("suppliers/<int:pk>/delete/", perm("delete_supplier", views.SupplierDeleteView.as_view()), name="supplier_delete"),

    # Customers
    path("customers/", perm("view_customer", views.CustomerListView.as_view()), name="customer_list"),
    path("customers/add/", perm("add_customer", views.CustomerCreateView.as_view()), name="customer_create"),
    path("customers/<int:pk>/edit/", perm("change_customer", views.CustomerUpdateView.as_view()), name="customer_update"),
    path("customers/<int:pk>/delete/", perm("delete_customer", views.CustomerDeleteView.as_view()), name="customer_delete"),

    # Sales
    path("sales/", perm("view_sale", views.SaleListView.as_view()), name="sale_list"),
    path("sales/new/", perm("add_sale", views.sale_create), name="sale_create"),
    path("sales/<int:pk>/", perm("view_sale", views.SaleDetailView.as_view()), name="sale_detail"),
    path("sales/<int:pk>/edit/", perm("change_sale", views.SaleUpdateView.as_view()), name="sale_update"),
    path("sales/<int:pk>/delete/", perm("delete_sale", views.SaleDeleteView.as_view()), name="sale_delete"),
]
