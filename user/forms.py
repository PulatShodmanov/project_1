from django import forms
from user.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        label=False,
        widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "Ism Familiya"}),
        help_text="Ism va Familyani kiriting.",
    )
    phone = forms.CharField(
        label=False,
        widget=forms.TextInput(attrs={"class": "form-control mb-3", "placeholder": "Telefon raqam"}),
        help_text="Telefon raqamni kiriting.",
    )
    password1 = forms.CharField(
        label=_("Parol"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control mb-3", "placeholder": "*********", "autocomplete": "newpassword"}),
        help_text="<small> Katta va kichik <b>harflar</b> , <b>raqamlar</b>, <b>8ta</b> belgidan iborat bo'lish kerak!</small>"
        )
    password2 = forms.CharField(
        label=_("Parolni takrorlang"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "*********", "autocomplete": "newpassword"}),
        help_text=_("Yuqoridagi parol bilan bir xil qilib yozing."),
        )

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not  phone.isdigit():
            raise ValidationError(
                _("Telefon raqami faqat raqamlar iborat bo'sin.")
            )
        if User.objects.filter(phone=phone).exists():
            raise ValidationError(
                _("Ushbu raqam allaqachon ishlatildan.")
            )
        if not len(phone) <= 9:
            raise ValidationError(
                _("Iltimos raqamni to'g'ri kiriting")
            )
        return phone
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("Iltimos parolni to'g'ri kiriting"), code="password_mismatch"
            )
        return password2
    
    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user
    




    