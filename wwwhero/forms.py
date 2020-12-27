from django import forms

from .models import Character


class CharacterCreateForm(forms.Form):
    name = forms.CharField(label="Character name", max_length=64)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Character.objects.filter(name=name, user=self.user).exists():
            raise forms.ValidationError('The character [%s] already exists' % name)
        return name
