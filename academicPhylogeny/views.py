# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import frequently_asked_question, connection, person, specialization
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from forms import SchoolForm, PersonForm

# Create your views here.
class HomePageView(TemplateView):
    template_name = "splash.html"

class PersonTemplateView(TemplateView):
    template_name = "person_search_skeleton.html"

    def get_context_data(self, **kwargs):
        context=super(PersonTemplateView, self).get_context_data(**kwargs)
        context["SchoolForm"]=SchoolForm()
        context["PersonForm"]=PersonForm()
        context["specializations"] = specialization.objects.all()
        return context


class PersonListView(ListView):
    template_name = "person_search_results.html"
    model = person

    def get_queryset(self, **kwargs):
        filterArgs = {}
        for key, value in self.request.GET.iteritems():
            if value:
                if value <> "":
                    filterArgs[key] = value
        return person.objects.filter(**filterArgs)

def person_numeric_detail_view(request, pk):
    ##if you ask for a detail view with a numeric parameter, translate it and
    ## return corresponding non numeric view
    try:
        requestedPerson=person.objects.get(pk=pk)
    except:
        return HttpResponseRedirect("/people/")
    return HttpResponseRedirect("/detail/" + requestedPerson.URL_for_detail)


class PersonDetailView(TemplateView):
    template_name = "person_detail.html"

    def get_context_data(self, **kwargs):
        URL_for_detail = self.kwargs["URL_for_detail"]
        try:
            thePerson = person.objects.get(URL_for_detail__exact=URL_for_detail)
        except ObjectDoesNotExist:
            thePerson = None

        try:
            advisorConnection = connection.objects.get(student__id=thePerson.id)
        except:
            advisorConnection = None

        try:
            studentConnections = connection.objects.filter(advisor__id=thePerson.id).order_by("student__yearOfPhD")
        except:
            studentConnections = None

        context = super(PersonDetailView, self).get_context_data(**kwargs)
        context["thePerson"] = thePerson
        context["advisorConnection"] = advisorConnection
        context["studentConnections"] = studentConnections
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
    template_name = "tree.html"

    def get_context_data(self, **kwargs):
        try:
            selectedNameID = self.kwargs["selectedNameID"]
        except:
            selectedNameID = None

        context = super(TreeView, self).get_context_data(**kwargs)
        selectedPersonHasNoConnections = False
        if selectedNameID:

            try:
                selectedPerson = person.objects.get(pk=selectedNameID)
                if connection.objects.filter(student=selectedPerson).count() == 0 and connection.objects.filter(
                        advisor=selectedPerson).count() == 0:
                    selectedPersonHasNoConnections = True

            except ObjectDoesNotExist:
                messages.add_message(request, messages.INFO,
                                     "Sorry, I can't find that person. Showing the whole tree instead")
                selectedPerson = None
                selectedNameID = None


        else:
            selectedNameID = None
            selectedPerson = None
        context["selectedPersonHasNoConnections"]=selectedPersonHasNoConnections
        context["selectedNameID"]=selectedNameID
        context["selectedPerson"]=selectedPerson
        return context


def JSONstream(request,selectedNameID=None):
    if selectedNameID != None:
        selectedNameID = int(selectedNameID)
        if connection.objects.filter(student = selectedNameID).count() == 0 and connection.objects.filter(advisor = selectedNameID).count() == 0:
            return HttpResponse("This person has no matching connections")
    advisors=[]
    students=[]
    studentIDs=[]
    advisorIDs=[]
    urlsForLink=[]
    for each in connection.objects.all():
        for advisor in each.advisor.all():
            advisors.append(advisor.firstName + " " + advisor.lastName)
            students.append(each.student.firstName + " " + each.student.lastName)
            studentIDs.append(each.student.id)
            advisorIDs.append(advisor.id)
            urlsForLink.append("/detail/" + each.student.URL_for_detail)
    links=zip(advisorIDs,studentIDs)
    parents, children = zip(*links)
    root_nodes = {x for x in parents if x not in children}
    for node in root_nodes:
        links.append(("", node))

    def get_nodes(node,selectedNameID=None):
        d = {}

        if node=="":
            d['name'] = ""
        else:
            try:
                d['name'] = students[studentIDs.index(node)]
            except:
                d['name'] = advisors[advisorIDs.index(node)]


        if node=="":
            d["link"] = "/search/"
        else:
            try:
                d["link"] = urlsForLink[studentIDs.index(node)]
            except:
                d['link'] = "/detail/" + advisors[advisorIDs.index(node)].replace(" ","_")


        try:
            if(get_parent(node)== ""):
                d["nodeType"] = "localRoot"
            else:
                temp=[each == node for each in children]
                if sum(temp) > 1:
                    d["nodeType"] = "coAdvisee"
                if sum(temp) == 1:
                    d["nodeType"] = "normal"
        except:
            if node == "root":
                d["nodeType"] = "root"

            else:
                d["nodeType"] = "none"


        if d["name"] != "":
            if selectedNameID:
                try:
                    if d['name'] == students[studentIDs.index(selectedNameID)]:
                        d["selected"] = "y"
                        d["xOffset"] = 17
                except:
                    if d['name'] == advisors[advisorIDs.index(selectedNameID)]:
                        d["selected"] = "y"
                        d["xOffset"] = 17
                    else:
                        d["selected"] = "n"
                        d["xOffset"] = 10
            else:
                d["selected"] = "n"
                d["xOffset"] = 10
        else:
            d["selected"] = "n"
            d["xOffset"] = 10


        if get_children(node):
            d['children'] = [get_nodes(child,selectedNameID) for child in get_children(node)]
        return d

    def get_children(node):
        return [x[1] for x in links if x[0] == node]

    def get_parent(node):
        return [x[0] for x in links if x[1] == node][0]

    originalSelection = selectedNameID

    matches = [selectedNameID == child for child in children]
    nAdvisors = sum(matches)

    if selectedNameID != None:
        if nAdvisors > 1:
            tree = get_nodes("",selectedNameID)
        else:
            while get_parent(selectedNameID) != "":
                selectedNameID = get_parent(selectedNameID)
            tree = get_nodes(selectedNameID,selectedNameID = originalSelection)
    else:
        tree=get_nodes("")


    return JsonResponse(tree)
