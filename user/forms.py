from django import forms
from user.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ngettext
from django.core.exceptions import ValidationError
from django.utils.text import capfirst


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
            except ValidationError:
                raise ValidationError(
                ngettext(
                    "Ushbu parol juda kalta. U kamida 8ta belgini o'z ichiga olishi kerak ",
                    "Ushbu parol juda kalta. It must contain at least ",
                    self.min_length,
                ),
                code="passsword_too_short",
                params={"min_length": self.min_length},
                )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user 
    
class CustomLoginForm(AuthenticationForm):
    phone = forms.CharField(max_length=15,
        required=True, 
        help_text="<small>Bo'sh</b> joylarisiz va <b>(+998)</b> kerak emas</small>", 
        label=_("Telefon"), 
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': '93-123-45-67', 'type': "tel"})
        )
    password = forms.CharField(
        label = _("Parol"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Parol', 'type': "password"})
        )
    
    error_message = {
        "invalid_login": _(
            "Iltimos to'gri raqam yoki parol kiriting."
        ),
        "inactive": _("Ushbu account faol emas."),
    }

    def __init__(self , request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'] = self.fields.pop('phone')
        self.fields['username'].widget.attrs['placeholder'] = _('Telefon')

        if self.fields["username"].label is None:
            self.fields["username"].label = capfirst(
                self.fields["username"].verbose_name
            )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, phone=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
    
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                self.error_message["inactive"],
                code="inactive",
            )
        
    def get_user(self):
        return self.user_cache
    

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_message["invalid_login"],
            code="invalid_login",
            params={"phone": self.fields["username"].label},
        )
    