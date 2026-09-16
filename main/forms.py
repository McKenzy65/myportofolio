from django.forms import ModelForm
from main.models import Certification

class CertificationForm(ModelForm):
    class Meta:
        model = Certification
        fields = ['title', 'description', 'year', 'is_highlight']