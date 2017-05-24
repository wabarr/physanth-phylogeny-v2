# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import frequently_asked_question, specialization, PhD, suggestedPhDTextUpdate, school, userContact
from django.db.models import Count
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from forms import SchoolForm, PhD_form_for_ajax_selects_search, suggestedPhDTextUpdateForm, PhDAddForm, UserContactAddForm
import json


# Create your views here.

def debug_view(ob):
    ###Just used to be able to debug the methods on my models
    wol=PhD.objects.get(lastName="Wolpoff")
    return JsonResponse(wol.get_nested_tree_dict)

class TrendsView(TemplateView):
    template_name = "trends.html"
    def get_context_data(self, **kwargs):
        context = super(TrendsView, self).get_context_data(**kwargs)
        # PhD per Year
        PhDsPerYear = PhD.objects.filter(validated=True, year__gt=1959).exclude(year__isnull=True).values('year').order_by('year').annotate(Count('year'))
        context["phdYearChartData"] = json.dumps(list(PhDsPerYear))

        #schools
        schoolCounts = school.objects.exclude(name="Unknown").annotate(num_phds=Count('phd')).filter(num_phds__gt=14).order_by("-num_phds").values()
        context["schoolCounts"] = json.dumps(list(schoolCounts))

        # specializations
        specializationCounts = specialization.objects.all().annotate(count=Count("phd")).order_by("-count").values()
        context["specializationCounts"] = json.dumps(list(specializationCounts))
        return context

class ThanksView(TemplateView):
    template_name = "thanks.html"

class HomePageView(TemplateView):
    template_name = "splash.html"

class PhDTemplateView(TemplateView):
    template_name = "PhD_search_skeleton.html"

    def get_context_data(self, **kwargs):
        context=super(PhDTemplateView, self).get_context_data(**kwargs)
        context["SchoolForm"]=SchoolForm()
        context["PhD_form_for_ajax_selects_search"]=PhD_form_for_ajax_selects_search()
        context["specializations"] = specialization.objects.all()
        return context

class suggestedPhDTextUpdateCreateView(CreateView):
    model = suggestedPhDTextUpdate
    form_class = suggestedPhDTextUpdateForm
    success_url = "/"

class ContactView(CreateView):
    model = userContact
    form_class = UserContactAddForm
    success_url = "/thanks/"

class AddPhDView(CreateView):
    model = PhD
    form_class = PhDAddForm
    success_url = "/thanks/"

class PhDListView(ListView):
    template_name = "PhD_search_results.html"
    model = PhD

    def get_queryset(self, **kwargs):
        filterArgs = {}
        for key, value in self.request.GET.iteritems():
            if value:
                if value <> "":
                    filterArgs[key] = value
        return PhD.objects.filter(**filterArgs)

def PhD_numeric_detail_view(request, pk):
    ##if you ask for a detail view with a numeric parameter, translate it and
    ## return corresponding non numeric view
    try:
        requestedPerson=PhD.objects.exclude(validated=False).get(pk=pk)
    except:
        return HttpResponseRedirect("/people/")
    return HttpResponseRedirect("/detail/" + requestedPerson.URL_for_detail)

class PhDDetailView(TemplateView):
    template_name = "PhD_detail.html"

    def get_context_data(self, **kwargs):
        URL_for_detail = self.kwargs["URL_for_detail"]
        try:
            thePhD = PhD.objects.exclude(validated=False).get(URL_for_detail__exact=URL_for_detail)
            students = PhD.objects.filter(advisor__id=thePhD.id)
        except:
            thePhD = None
            students = None


        context = super(PhDDetailView, self).get_context_data(**kwargs)
        context["thePhD"] = thePhD
        context["students"] = students
        return context

class AboutView(TemplateView):
    template_name = "about.html"

class FAQView(TemplateView):
    template_name = "FAQ.html"

    def get_context_data(self, **kwargs):
        context = super(FAQView, self).get_context_data(**kwargs)
        context['FAQs'] = frequently_asked_question.objects.filter(published=True)
        return context


class TreeView(TemplateView):
    template_name = 'tree.html'

    def get_context_data(self, **kwargs):
        context = super(TreeView, self).get_context_data(**kwargs)
        try:
            context['pk'] = self.kwargs["pk"]
            context['selectedName'] = PhD.objects.get(pk=self.kwargs["pk"]).__unicode__()
        except:
            context['pk'] = None
            context['selectedName'] = None
        return context


def tree_JSON(request, pk=None):
    if pk is not None:
        thePerson=PhD.objects.get(pk=pk)
        theRoots = thePerson.find_root_ancestors
        if len(theRoots) > 1:
            rootNode = {"name":"root_node", "children":[]}
            for root in theRoots:
                rootNode["children"].append(root.get_nested_tree_dict)
            return JsonResponse(rootNode)
        else:
            return JsonResponse(theRoots[0].get_nested_tree_dict)
    else:
        allRoots = []
        for eachPhD in PhD.objects.all():
            if len(eachPhD.advisor.all()) > 0:
                pass
            else:
                allRoots.append(eachPhD)
        rootNode = {"name": "root_node", "children": []}
        for root in allRoots[0:15]:
            rootNode["children"].append(root.get_nested_tree_dict)
        return JsonResponse(rootNode)

