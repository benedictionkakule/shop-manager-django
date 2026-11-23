from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Category, Customer, Product, Sale, SaleItem, Supplier


class BootstrapFormMixin:
    """Adds Bootstrap classes to every field of a form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = css


class ProductForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "supplier", "price",
                  "quantity", "reorder_level", "image"]


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class SupplierForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "phone", "email", "address"]


class CustomerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email"]


class SaleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["customer", "notes"]


class SaleItemForm(BootstrapFormMixin, forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = SaleItem
        fields = ["product", "quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only offer products that are actually in stock
        self.fields["product"].queryset = Product.objects.filter(quantity__gt=0)
        self.fields["product"].label_from_instance = (
            lambda p: f"{p.name} - {p.price} ({p.quantity} in stock)"
        )


class BaseSaleItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        # Total quantity requested per product (the same product may appear twice)
        requested = {}
        for form in self.forms:
            if not form.cleaned_data:
                continue
            product = form.cleaned_data["product"]
            requested[product] = requested.get(product, 0) + form.cleaned_data["quantity"]

        if not requested:
            raise forms.ValidationError("Add at least one item to the sale.")

        for product, qty in requested.items():
            if qty > product.quantity:
                raise forms.ValidationError(
                    f"Not enough stock for {product.name}: "
                    f"{product.quantity} available, {qty} requested."
                )


SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem,
    form=SaleItemForm,
    formset=BaseSaleItemFormSet,
    extra=5,
    can_delete=False,
)

# ---------- Sign-up form ----------
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email")
