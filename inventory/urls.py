from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.urls import path
from django.views.generic import RedirectView
from . import admin_tools
from . import accounts, reports, views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),
        path("favicon.ico", login_not_required(RedirectView.as_view(url="/static/favicon.ico")), name="favicon"),
        path("admin-tools/clear-recent-actions/", admin_tools.clear_recent_actions, name="clear_recent_actions"),

    # Authentication
    path("login/", login_not_required(auth_views.LoginView.as_view(
        template_name="registration/login.html",
        redirect_authenticated_user=True,
    )), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", accounts.signup, name="signup"),

    # Dashboard and reports
    path("dashboard/", reports.dashboard, name="dashboard"),
    path("reports/sales/", reports.sales_report, name="sales_report"),

    # Products
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/add/", views.ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),

    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Suppliers
    path("suppliers/", views.SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/add/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("suppliers/<int:pk>/edit/", views.SupplierUpdateView.as_view(), name="supplier_update"),
    path("suppliers/<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),

    # Customers
    path("customers/", views.CustomerListView.as_view(), name="customer_list"),
    path("customers/add/", views.CustomerCreateView.as_view(), name="customer_create"),
    path("customers/<int:pk>/edit/", views.CustomerUpdateView.as_view(), name="customer_update"),
    path("customers/<int:pk>/delete/", views.CustomerDeleteView.as_view(), name="customer_delete"),

    # Sales
    path("sales/", views.SaleListView.as_view(), name="sale_list"),
    path("sales/new/", views.sale_create, name="sale_create"),
    path("sales/<int:pk>/", views.SaleDetailView.as_view(), name="sale_detail"),
    path("sales/<int:pk>/edit/", views.SaleUpdateView.as_view(), name="sale_update"),
    path("sales/<int:pk>/delete/", views.SaleDeleteView.as_view(), name="sale_delete"),
]
