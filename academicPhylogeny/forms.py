from django.forms import ValidationError
from django.contrib.auth.models import User as UserTable
from django.forms import ModelForm, CharField, EmailField, Form, ModelChoiceField
from django.forms.widgets import PasswordInput
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from .models import *


class SchoolAddForm(ModelForm):
    class Meta:
        model = school
        fields = ('name',)

class SchoolForm(ModelForm):

    class Meta:
        model = school
        fields=["search_by_school"]

    search_by_school = AutoCompleteSelectField("school",required=False, help_text=None)

class PhDAddForm(ModelForm):
    class Meta:
        model = PhD
        fields = ["firstName","lastName","year","school","advisor","specialization", "id", "submitter_email", "source_of_info", "submitter_user"]
    school = AutoCompleteSelectField("school", help_text=None)
    advisor = AutoCompleteSelectMultipleField("PhD", required=True, help_text=None)

class PhD_form_for_ajax_selects_search(ModelForm):

    class Meta:
        model = PhD
        fields=["search_by_name"]

    search_by_name = AutoCompleteSelectField("PhD",required=False, help_text=None)

class PhDEditForm(ModelForm):
    #for authenticated users to edit their own entries
    class Meta:
        model=PhD
        fields = ["firstName", "lastName", "year", "school", "advisor", "specialization", "id"]
    school = AutoCompleteSelectField("school", help_text=None)
    advisor = AutoCompleteSelectMultipleField("PhD", required=True, help_text=None)

class PhDUpdateForm(ModelForm):
    #for unauthenticated users to suggest entries that require moderator validation
    class Meta:
        model=PhDupdate
        fields = ["suggested_update_fixture", "submitter_email", "source_of_info", "PhD",  "submitter_user"]

#class suggestedPhDTextUpdateForm(ModelForm):

#    class Meta:
#       model = suggestedPhDTextUpdate
#        fields = ["PhD", "field", "value"]

#    PhD = AutoCompleteSelectField("PhD",required=True, help_text=None)
#    field = forms.ChoiceField(choices = CHOICES_editable_fields)

class UserContactAddForm(ModelForm):
    class Meta:
        model=userContact
        exclude=["dealt_with","admin_notes","date_last_modified","date_sent"]

class UserCreateForm(ModelForm):
    class Meta:
        model=User
        fields=('username', 'first_name','last_name', 'email', 'password')
    username = CharField(required=True)
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    email = EmailField(required=True)
    password = CharField(widget=PasswordInput, required=True)

    def clean(self):
        cleaned_data = super(UserCreateForm, self).clean()
        theEmail = cleaned_data["email"]
        existingUser = UserTable.objects.filter(email=theEmail)
        if existingUser.count() > 0:
            raise ValidationError("Error: This email address is already associated with a user account")


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields=('user',"associated_PhD")
    associated_PhD = AutoCompleteSelectField("PhD", required=True, help_text=None, label="Search")

class UserProfileEditForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('current_position','current_affiliation', "research_website", 'research_blurb')

class PhDValidateForm(ModelForm):
    class Meta:
        model = PhD
        fields = ["firstName", "lastName", "specialization", "year", "school", "advisor", "id"]
    #advisor = AutoCompleteSelectField("PhD", required=True, help_text=None)

class MailingListOptInForm(Form):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    email = EmailField(required=True)

class SpecializationForm(Form):
    specialization = ModelChoiceField(specialization.objects.all())