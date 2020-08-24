from django import forms
from django.core.exceptions import ValidationError

from encyclopedia import util


class CreateEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label='Content', widget=forms.Textarea)

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title is not None and util.get_entry(title) is not None:
            raise ValidationError("Title already exists.")

        return title


class EditEntryForm(forms.Form):
    content = forms.CharField(label='Content', widget=forms.Textarea)
