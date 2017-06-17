from django import forms
from django.forms import ModelForm
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from .models import *

class SchoolForm(ModelForm):

    class Meta:
        model = school
        fields=["search_by_school"]

    search_by_school = AutoCompleteSelectField("school",required=False, help_text=None)

class PhDAddForm(ModelForm):
    class Meta:
        model = PhD
        fields = ["firstName","lastName","year","school","advisor","specialization", "id"]
    school = AutoCompleteSelectField("school", help_text=None)
    advisor = AutoCompleteSelectMultipleField("PhD", required=True, help_text=None)

class PhD_form_for_ajax_selects_search(ModelForm):

    class Meta:
        model = PhD
        fields=["search_by_name"]

    search_by_name = AutoCompleteSelectField("PhD",required=False, help_text=None)

class PhDUpdateForm(ModelForm):
    class Meta:
        model=PhDupdate
        fields = ["suggested_update_fixture"]

class suggestedPhDTextUpdateForm(ModelForm):

    class Meta:
        model = suggestedPhDTextUpdate
        fields = ["PhD", "field", "value"]

    PhD = AutoCompleteSelectField("PhD",required=True, help_text=None)
    #field = forms.ChoiceField(choices = CHOICES_editable_fields)

class UserContactAddForm(ModelForm):
    class Meta:
        model=userContact
        exclude=["dealt_with","admin_notes","date_last_modified","date_sent"]