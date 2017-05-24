# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from academicPhylogeny.models import *
from ajax_select import make_ajax_form

# Register your models here.

class UserContactAdmin(admin.ModelAdmin):
    search_fields = ["last_name","first_name","message", "email"]
    list_display = ["last_name","first_name","date_sent",'dealt_with']

class PhDAdmin(admin.ModelAdmin):
    search_fields = ["lastName","firstName"]
    list_filter = ["school"]
    list_display = ["id","firstName", "lastName","year", "school", "validated"]
    form = make_ajax_form(PhD, {
        'advisor': 'PhD',  # ManyToManyField
        'school': 'school',  # ForeignKeyField
        'specialization': 'specialization'
    })
class SchoolAdmin(admin.ModelAdmin):
    search_fields = ["name",]
    list_display = ["id","name"]


class FAQadmin(admin.ModelAdmin):
    list_display = ("heading","published","displayOrder")
    list_filter = ("published",)
    list_editable = ("published","displayOrder")

class SuggestedPhDTexaUpdateAdmin(admin.ModelAdmin):
    list_display = ["PhD", "field", "value", "moderator_approved", "approver"]
    form = make_ajax_form(suggestedPhDTextUpdate, {
        'PhD': 'PhD'
    })

admin.site.register(frequently_asked_question,FAQadmin)
admin.site.register(school, SchoolAdmin)
#admin.site.register(person, admin.ModelAdmin)
admin.site.register(PhD, PhDAdmin)
admin.site.register(userContact, UserContactAdmin)
admin.site.register(suggestedPhDTextUpdate, SuggestedPhDTexaUpdateAdmin)
