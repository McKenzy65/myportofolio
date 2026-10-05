from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.html import strip_tags

from main.models import Certification


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
