# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from academicPhylogeny.models import *

# Register your models here.

class SchoolAdmin(admin.ModelAdmin):
    search_fields = ["Name",]


class FAQadmin(admin.ModelAdmin):
    list_display = ("heading","published","displayOrder")
    list_filter = ("published",)
    list_editable = ("published","displayOrder")

admin.site.register(frequently_asked_question,FAQadmin)
admin.site.register(school, SchoolAdmin)
admin.site.register(person, admin.ModelAdmin)