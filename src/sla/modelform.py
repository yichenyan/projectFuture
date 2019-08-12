from django import forms
from .models import DartOpsReport

class UploadFileModelForm(forms.ModelForm):
    class Meta:
        model = DartOpsReport
        fields = "__all__"



