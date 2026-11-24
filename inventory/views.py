from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from .notifications import notify_sale
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import (
    CategoryForm, CustomerForm, ProductForm, SaleForm, SaleItemFormSet,
    SupplierForm,
)
from .models import Category, Customer, Product, Sale, Supplier


# ---------- Shared building blocks ----------

class PageTitleMixin:
    page_title = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.page_title
        return ctx


class SafeDeleteView(DeleteView):
    """Delete view that shows a friendly message if the record is protected."""
    template_name = "inventory/confirm_delete.html"
    success_message = "Record deleted."
    protected_message = "This record is in use and can't be deleted."

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return redirect(self.success_url)
        messages.success(self.request, self.success_message)
        return response


# ---------- Products ----------

class ProductListView(ListView):
    model = Product
    template_name = "inventory/product_list.html"
    paginate_by = 10

    def get_queryset(self):
        qs = Product.objects.select_related("category", "supplier")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "inventory/product_detail.html"


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Product added successfully.")
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully.")
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "inventory/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "This product appears in past sales, so it can't be deleted.",
            )
            return redirect("product_detail", pk=self.object.pk)
        messages.success(self.request, "Product deleted.")
        return response


# ---------- Categories ----------

class CategoryListView(ListView):
    model = Category
    template_name = "inventory/category_list.html"
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.annotate(num_products=Count("products"))


class CategoryCreateView(PageTitleMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("category_list")
    success_message = "Category added."
    page_title = "Add category"


class CategoryUpdateView(PageTitleMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("category_list")
    success_message = "Category updated."
    page_title = "Edit category"


class CategoryDeleteView(SafeDeleteView):
    model = Category
    success_url = reverse_lazy("category_list")
    success_message = "Category deleted."
    protected_message = "This category still has products, so it can't be deleted."


# ---------- Suppliers ----------

class SupplierListView(ListView):
    model = Supplier
    template_name = "inventory/supplier_list.html"
    paginate_by = 10


class SupplierCreateView(PageTitleMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("supplier_list")
    success_message = "Supplier added."
    page_title = "Add supplier"


class SupplierUpdateView(PageTitleMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("supplier_list")
    success_message = "Supplier updated."
    page_title = "Edit supplier"


class SupplierDeleteView(SafeDeleteView):
    model = Supplier
    success_url = reverse_lazy("supplier_list")
    success_message = "Supplier deleted."


# ---------- Customers ----------

class CustomerListView(ListView):
    model = Customer
    template_name = "inventory/customer_list.html"
    paginate_by = 10


class CustomerCreateView(PageTitleMixin, SuccessMessageMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("customer_list")
    success_message = "Customer added."
    page_title = "Add customer"


class CustomerUpdateView(PageTitleMixin, SuccessMessageMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("customer_list")
    success_message = "Customer updated."
    page_title = "Edit customer"


class CustomerDeleteView(SafeDeleteView):
    model = Customer
    success_url = reverse_lazy("customer_list")
    success_message = "Customer deleted."


# ---------- Sales ----------

class SaleListView(ListView):
    model = Sale
    template_name = "inventory/sale_list.html"
    paginate_by = 10

    def get_queryset(self):
        return Sale.objects.select_related("customer", "served_by").prefetch_related(
            "items__product"
        )


class SaleDetailView(DetailView):
    model = Sale
    template_name = "inventory/sale_detail.html"


def sale_create(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST, prefix="items")

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():  # all-or-nothing
                sale = form.save(commit=False)
                if request.user.is_authenticated:
                    sale.served_by = request.user
                sale.save()

                formset.instance = sale
                for item in formset.save(commit=False):
                    product = Product.objects.get(pk=item.product_id)
                    item.unit_price = product.price      # freeze today's price
                    item.save()
                    product.quantity -= item.quantity    # reduce stock
                    product.save(update_fields=["quantity", "updated_at"])
            notify_sale(sale)  # receipt + low-stock alert

            messages.success(request, f"Sale #{sale.pk} recorded. Total: {sale.total}")
            return redirect("sale_detail", pk=sale.pk)
    else:
        form = SaleForm()
        formset = SaleItemFormSet(prefix="items")

    return render(request, "inventory/sale_form.html", {"form": form, "formset": formset})


class SaleUpdateView(PageTitleMixin, SuccessMessageMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("sale_list")
    success_message = "Sale updated."
    page_title = "Edit sale (customer and notes only)"


class SaleDeleteView(DeleteView):
    model = Sale
    template_name = "inventory/confirm_delete.html"
    success_url = reverse_lazy("sale_list")

    def form_valid(self, form):
        with transaction.atomic():
            # Put the stock back before the sale disappears
            for item in self.object.items.select_related("product"):
                product = item.product
                product.quantity += item.quantity
                product.save(update_fields=["quantity", "updated_at"])
            response = super().form_valid(form)
        messages.success(self.request, "Sale deleted and stock restored.")
        return response
