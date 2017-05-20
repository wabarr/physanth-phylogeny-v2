# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from academicPhylogeny.models import *
from ajax_select import make_ajax_form

# Register your models here.

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
    search_fields = ["Name",]


class FAQadmin(admin.ModelAdmin):
    list_display = ("heading","published","displayOrder")
    list_filter = ("published",)
    list_editable = ("published","displayOrder")

admin.site.register(frequently_asked_question,FAQadmin)
admin.site.register(school, SchoolAdmin)
#admin.site.register(person, admin.ModelAdmin)
admin.site.register(PhD, PhDAdmin)