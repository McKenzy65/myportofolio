from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.html import strip_tags
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from main.models import Certification


class PortfolioAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Username atau kata sandi belum sesuai. Periksa lagi dan coba kembali.",
        "inactive": "Akun ini belum aktif.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"placeholder": "Masukkan username", "autocomplete": "username"})
        self.fields["password"].label = "Kata sandi"
        self.fields["password"].widget.attrs.update({"placeholder": "Masukkan kata sandi", "autocomplete": "current-password"})


class PortfolioUserCreationForm(UserCreationForm):
    error_messages = {"password_mismatch": "Konfirmasi kata sandi belum sama. Silakan ulangi."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Maksimal 150 karakter. Gunakan huruf, angka, atau karakter @ . + - _."
        self.fields["username"].widget.attrs.update({"placeholder": "Pilih username", "autocomplete": "username"})
        self.fields["password1"].help_text = (
            "<ul><li>Minimal 8 karakter.</li><li>Jangan gunakan kata sandi yang terlalu umum.</li>"
            "<li>Hindari kemiripan dengan informasi pribadi.</li><li>Jangan hanya menggunakan angka.</li></ul>"
        )
        self.fields["password2"].help_text = "Masukkan kembali kata sandi yang sama untuk konfirmasi."
        for name, label, placeholder in (
            ("password1", "Kata sandi", "Buat kata sandi"),
            ("password2", "Konfirmasi kata sandi", "Ulangi kata sandi"),
        ):
            self.fields[name].label = label
            self.fields[name].widget.attrs.update({"placeholder": placeholder, "autocomplete": "new-password"})


class CertificationForm(ModelForm):
    class Meta:
        model = Certification
        fields = ['title', 'description', 'year', 'is_highlight']

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Judul sertifikasi tidak boleh hanya berisi tag HTML.")
        return title

    def clean_description(self):
        description = strip_tags(self.cleaned_data["description"]).strip()
        if not description:
            raise ValidationError("Deskripsi sertifikasi tidak boleh hanya berisi tag HTML.")
        return description
