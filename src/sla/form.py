from django import forms

class UploadOpsDataForm(forms.Form):
    #name = forms.CharField(max_length=50,min_length=3,required=True,label='File Name:')
    myfile = forms.FileField(label='Choose the downloaded spreadsheet:')  # TODO: 美化格式

