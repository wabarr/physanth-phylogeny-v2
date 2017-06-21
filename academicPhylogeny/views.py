# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import frequently_asked_question, specialization, PhD, PhDupdate, school, userContact, UserProfile
from django.db.models import Count, Value, F
from django.db.models.functions import Concat
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
import random
from forms import SchoolForm, PhD_form_for_ajax_selects_search, PhDUpdateForm, PhDAddForm, PhDEditForm, UserContactAddForm, UserCreateForm, UserProfileForm
import json

# Create your views here.



def randomPerson(request):
    nRecords = PhD.objects.count()
    randomPerson = PhD.objects.all()[random.randint(0, nRecords-1)]
    return HttpResponseRedirect("/detail/" + randomPerson.URL_for_detail)

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

class SubmitPhDUpdateView(TemplateView):
    # This view is for users to submit suggested updates
    # it binds a specific PhD objet to be edited
    # template suggest_edit_phd.html actually submits a POST request to
    # PhDUpdateView to create the suggested update from the bound PhD object data

    template_name = "suggest_edit_phd.html"

    def get_context_data(self, **kwargs):
        context = super(SubmitPhDUpdateView, self).get_context_data(**kwargs)

        try:
            thePerson = PhD.objects.get(pk=self.kwargs["pk"])
            context["selectedID"] = thePerson.id
            context["selected_PhD_form"] = PhDAddForm(instance=thePerson)
            context["form"] = PhDUpdateForm()
            return context
        except:
            return context

class UserCreateView(CreateView):
    model = User
    form_class = UserCreateForm
    success_url = "/user_created/"

    def form_valid(self, form):
        response = super(UserCreateView, self).form_valid(form)
        pw=form.data["password"]
        self.object.set_password(pw)
        self.object.save()
        return response


class ClaimPhDView(CreateView):
    model = UserProfile
    form_class = UserProfileForm
    success_url = "/"

    def get_initial(self):
        return {'user': self.request.user}

    def get_context_data(self, **kwargs):
        context = super(ClaimPhDView, self).get_context_data(**kwargs)
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
            context["user_profile"] = user_profile
        except:
            pass
        return context

class UserCreatedView(TemplateView):
    template_name = "user_created.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserCreatedView, self).dispatch(*args, **kwargs)

class PhDUpdateView(CreateView):
    # for unauthenticated users to suggest entries that require moderator validation
    model = PhDupdate
    form_class = PhDUpdateForm
    template_name = "unauthenticated_user_PhDupdate.html"
    success_url = "/thanks/"

class PhD_EditView(UpdateView):
    ## for authenticated users to edit their own entries
    model = PhD
    form_class = PhDEditForm
    template_name = "authenticated_user_PhD_edit.html"

    def get_context_data(self, **kwargs):
        context = super(PhD_EditView, self).get_context_data(**kwargs)
        try:
            context["user_profile"] = UserProfile.objects.get(associated_PhD=self.object)
        except:
            pass
        return context

    def get_success_url(self):
        return "/detail/" + str(self.object.id) +  "/"

class ContactView(CreateView):
    model = userContact
    form_class = UserContactAddForm
    success_url = "/thanks/"

class PreAddPhDView(TemplateView):
    template_name = "pre_add_phd.html"

    def get_context_data(self, **kwargs):
        context=super(PreAddPhDView, self).get_context_data(**kwargs)
        context["form"] = PhD_form_for_ajax_selects_search()
        return context

class AddPhDView(CreateView):
    model = PhD
    form_class = PhDAddForm
    success_url = "/thanks/"
    template_name = "unauthenticated_user_PhDupdate.html"

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
            students = PhD.objects.filter(advisor__id=thePhD.id).order_by("year")
        except:
            thePhD = None
            students = None
        try:
            theUserProfile=UserProfile.objects.get(associated_PhD=thePhD)
        except:
            theUserProfile=None


        context = super(PhDDetailView, self).get_context_data(**kwargs)
        context["thePhD"] = thePhD
        context["students"] = students
        context["user_profile"] = theUserProfile
        context["nodes"]= thePhD.network_nodes_formatted
        context["edges"]= thePhD.network_edges_formatted

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

class NetworkView(TreeView):
    template_name = 'network.html'

    def get_context_data(self, **kwargs):
        context = super(TreeView, self).get_context_data(**kwargs)
        try:
            selectedPhD = PhD.objects.get(URL_for_detail=kwargs["URL_for_detail"])
        except:
            return context
        if not selectedPhD.validated:
            return context

        context["selectedPerson"] = selectedPhD
        context["nodes"]= selectedPhD.network_nodes_formatted
        context["edges"]= selectedPhD.network_edges_formatted

        return context

def getNetworkJSONView(request, pk):
    thePerson = PhD.objects.get(pk=pk)
    return HttpResponse(json.dumps({"edges":thePerson.network_edges_formatted, "nodes":thePerson.network_nodes_formatted}))


def networkViewNumeric(request, pk):
    ##if you ask for a newtork view with a numeric parameter, translate it and
    ## return corresponding non numeric view
    try:
        requestedPerson=PhD.objects.exclude(validated=False).get(pk=pk)
    except:
        return HttpResponseRedirect("/people/")
    return HttpResponseRedirect("/network/" + requestedPerson.URL_for_detail)

def tree_nodes_JSON(request):
    nodes = PhD.objects.all().filter(validated=True).annotate(name=Concat("firstName", Value(" "), "lastName")).values_list("id","name")
    return JsonResponse(list(nodes), safe=False)

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

