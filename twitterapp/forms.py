from django import forms

class TestForm(forms.Form):
    text = forms.CharField(label='ユーザー名')