# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import frequently_asked_question, specialization, PhD, suggestedPhDTextUpdate
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from forms import SchoolForm, PhD_form_for_ajax_selects_search, suggestedPhDTextUpdateForm, PhDAddForm

# Create your views here.

def debug_view(ob):
    ###Just used to be able to debug the methods on my models
    wol=PhD.objects.get(lastName="Wolpoff")
    return JsonResponse(wol.get_nested_tree_dict)

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
        context['pk'] = self.kwargs["pk"]
        context['selectedName'] = PhD.objects.get(pk=self.kwargs["pk"]).__unicode__()
        return context


def tree_JSON(request, pk):
    thePerson=PhD.objects.get(pk=pk)
    theRoots = thePerson.find_root_ancestors
    return JsonResponse(theRoots[0].get_nested_tree_dict)
# class TreeView(TemplateView):
#     template_name = "tree.html"
#
#     def get_context_data(self, **kwargs):
#         try:
#             selectedNameID = self.kwargs["selectedNameID"]
#         except:
#             selectedNameID = None
#
#         context = super(TreeView, self).get_context_data(**kwargs)
#         selectedPersonHasNoConnections = False
#         if selectedNameID:
#
#             try:
#                 selectedPerson = person.objects.get(pk=selectedNameID)
#                 if connection.objects.filter(student=selectedPerson).count() == 0 and connection.objects.filter(
#                         advisor=selectedPerson).count() == 0:
#                     selectedPersonHasNoConnections = True
#
#             except ObjectDoesNotExist:
#                 messages.add_message(request, messages.INFO,
#                                      "Sorry, I can't find that person. Showing the whole tree instead")
#                 selectedPerson = None
#                 selectedNameID = None
#
#
#         else:
#             selectedNameID = None
#             selectedPerson = None
#         context["selectedPersonHasNoConnections"]=selectedPersonHasNoConnections
#         context["selectedNameID"]=selectedNameID
#         context["selectedPerson"]=selectedPerson
#         return context
#
#
# def tree_JSON(request, pk):
#         theObject = PhD.objects.filter(pk=pk)
#         resp=serializers.serialize("json", theObject)
#         return JsonResponse(resp)
#     #except:
#      #   return JsonResponse({"error":"This person does not exist in the database."})
#
# def JSONstream(request,selectedNameID=None):
#     if selectedNameID != None:
#         selectedNameID = int(selectedNameID)
#         if connection.objects.filter(student = selectedNameID).count() == 0 and connection.objects.filter(advisor = selectedNameID).count() == 0:
#             return HttpResponse("This person has no matching connections")
#     advisors=[]
#     students=[]
#     studentIDs=[]
#     advisorIDs=[]
#     urlsForLink=[]
#     for each in connection.objects.all():
#         for advisor in each.advisor.all():
#             advisors.append(advisor.firstName + " " + advisor.lastName)
#             students.append(each.student.firstName + " " + each.student.lastName)
#             studentIDs.append(each.student.id)
#             advisorIDs.append(advisor.id)
#             urlsForLink.append("/detail/" + each.student.URL_for_detail)
#     links=zip(advisorIDs,studentIDs)
#     parents, children = zip(*links)
#     root_nodes = {x for x in parents if x not in children}
#     for node in root_nodes:
#         links.append(("", node))
#
#     def get_nodes(node,selectedNameID=None):
#         d = {}
#
#         if node=="":
#             d['name'] = ""
#         else:
#             try:
#                 d['name'] = students[studentIDs.index(node)]
#             except:
#                 d['name'] = advisors[advisorIDs.index(node)]
#
#
#         if node=="":
#             d["link"] = "/search/"
#         else:
#             try:
#                 d["link"] = urlsForLink[studentIDs.index(node)]
#             except:
#                 d['link'] = "/detail/" + advisors[advisorIDs.index(node)].replace(" ","_")
#
#
#         try:
#             if(get_parent(node)== ""):
#                 d["nodeType"] = "localRoot"
#             else:
#                 temp=[each == node for each in children]
#                 if sum(temp) > 1:
#                     d["nodeType"] = "coAdvisee"
#                 if sum(temp) == 1:
#                     d["nodeType"] = "normal"
#         except:
#             if node == "root":
#                 d["nodeType"] = "root"
#
#             else:
#                 d["nodeType"] = "none"
#
#
#         if d["name"] != "":
#             if selectedNameID:
#                 try:
#                     if d['name'] == students[studentIDs.index(selectedNameID)]:
#                         d["selected"] = "y"
#                         d["xOffset"] = 17
#                 except:
#                     if d['name'] == advisors[advisorIDs.index(selectedNameID)]:
#                         d["selected"] = "y"
#                         d["xOffset"] = 17
#                     else:
#                         d["selected"] = "n"
#                         d["xOffset"] = 10
#             else:
#                 d["selected"] = "n"
#                 d["xOffset"] = 10
#         else:
#             d["selected"] = "n"
#             d["xOffset"] = 10
#
#
#         if get_children(node):
#             d['children'] = [get_nodes(child,selectedNameID) for child in get_children(node)]
#         return d
#
#     def get_children(node):
#         return [x[1] for x in links if x[0] == node]
#
#     def get_parent(node):
#         return [x[0] for x in links if x[1] == node][0]
#
#     originalSelection = selectedNameID
#
#     matches = [selectedNameID == child for child in children]
#     nAdvisors = sum(matches)
#
#     if selectedNameID != None:
#         if nAdvisors > 1:
#             tree = get_nodes("",selectedNameID)
#         else:
#             while get_parent(selectedNameID) != "":
#                 selectedNameID = get_parent(selectedNameID)
#             tree = get_nodes(selectedNameID,selectedNameID = originalSelection)
#     else:
#         tree=get_nodes("")
#
#
#     return JsonResponse(tree)
