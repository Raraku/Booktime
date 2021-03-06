from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from main import forms
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, render
from main import models
import logging
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView


# Create your views here.
logger = logging.getLogger(__name__)


class ContactUsView(FormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs["tag"]
        self.tag = None
        if tag != "all":
            self.tag = get_object_or_404(models.ProductTag, slug=tag)
        if self.tag:
            products = models.Product.objects.active().filter(tags=self.tag)
        else:
            products = models.Product.objects.active()
        return products.order_by("name")


def signup(request):
    form = forms.UserCreationForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect("home")
    return render(request, "signup.html", {"form": form})


class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = ["name", "address1", "address2", "zip_code", "city", "country"]
    success_url = reverse_lazy("address_list")

    def form_valid(self, form, **kwargs):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    fields = ["name", "address1", "address2", "zip_code", "city", "country"]
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


def add_to_basket(request):
    product = get_object_or_404(models.Product, pk=request.GET.get("product_id"))
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id

    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(reverse("product", args=(product.slug,)))


def manage_basket(request):
    if not request.basket:
        return render(request, "basket.html", {"formset": None})

    if request.method == "POST":
        formset = forms.BasketLineFormSet(request.POST, instance=request.basket)
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(instance=request.basket)
    if request.basket.is_empty():
        return render(request, "basket.html", {"formset": None})

    return render(request, "basket.html", {"formset": formset})


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy("checkout_done")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session["basket_id"]
        basket = self.request.basket
        basket.create_order(
            form.cleaned_data["billing_address"], form.cleaned_data["shipping_address"]
        )
        return super().form_valid(form)


class DateInput(django_forms.DateInput):
    input_type = "date"


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order

        fields = {
            "user__email": ["icontains"],
            "status": ["exact"],
            "date_updated": ["gt", "lt"],
            "date_added": ["gt", "lt"],
        }
        filter_overrides = {
            django_models.DateTimeField: {
                "filter_class": django_filters.DateFilter,
                "extra": lambda f: {"widget": DateInput},
            }
        }


class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_staff is True
