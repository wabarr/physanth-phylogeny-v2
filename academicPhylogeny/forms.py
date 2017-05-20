from django import forms
from django.forms import ModelForm
from ajax_select.fields import AutoCompleteSelectField
from .models import school, PhD

class SchoolForm(ModelForm):

    class Meta:
        model = school
        fields=["search_by_school"]

    search_by_school = AutoCompleteSelectField("school",required=False, help_text=None)

class PhDForm(ModelForm):

    class Meta:
        model = PhD
        fields=["search_by_name"]

    search_by_name = AutoCompleteSelectField("PhD",required=False, help_text=None)

