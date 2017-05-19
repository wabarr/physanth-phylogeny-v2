from ajax_select import register, LookupChannel
from .models import school, person
from django.db.models import Value
from django.db.models.functions import Concat

@register('school')
class TagLookup(LookupChannel):

    model = school

    def get_query(self, q, request):
        return self.model.objects.filter(name__contains=q)

    def format_item_display(self, item):
        return u"<div class='chip school-chip'>%s</div>" % item.name

@register('person')
class PersonLookup(LookupChannel):

    model = person

    def get_query(self, q, request):
        queryset = person.objects.annotate(fullName=Concat('firstName',Value(' '),'lastName'))
        return queryset.filter(fullName__icontains=q)

    def format_item_display(self, item):
        return u"<div class='chip'>%s %s</div>" % (item.firstName, item.lastName)