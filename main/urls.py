"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from academicPhylogeny.views import *
from ajax_select import urls as ajax_select_urls
from django.views.generic import RedirectView

urlpatterns = [
    url('^', include('academicPhylogeny.registration_authorization_urls')),
    url(r'^admin/', admin.site.urls),
    ##user auth urls
    url(r'^create_user/', UserCreateView.as_view()),
    url(r'^user_created/', UserCreatedView.as_view()),
    url(r'^claim/', ClaimPhDView.as_view()),
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^contact/$', ContactView.as_view()),
    url(r'^thanks/$', ThanksView.as_view()),
    url(r'^trends/$', TrendsView.as_view()),
    url(r'^FAQ/', FAQView.as_view()),
    url(r'^about/', AboutView.as_view()),
    url(r'^people/', PhDTemplateView.as_view(), name="people_search"),
    url(r'^people_ajax/', PhDListView.as_view()),
    url(r'^submit/$', PreAddPhDView.as_view()),
    url(r'^submit_post_search/$', AddPhDView.as_view()),
    url(r'^suggest_change/(?P<pk>\d+)/$', SubmitPhDUpdateView.as_view()),
    url(r'^suggested_change/$', PhDUpdateView.as_view()),
    url(r'^random/', randomNetwork),
#    url(r'^getJSONconnections/(?P<selectedNameID>\d+)/$', JSONstream),
#    url(r'^getJSONconnections/$', JSONstream),
    #url(r'^tree_JSON/(?P<pk>\d+)/$', tree_JSON),
    #url(r'^tree_JSON/$', tree_JSON),
    #url(r'^tree_nodes_JSON/$',tree_nodes_JSON),
    #url(r'^tree/(?P<pk>\d+)/$', TreeView.as_view()),
    url(r'^get_network_JSON/(?P<pk>\d+)/$', getNetworkJSONView),
    url(r'^network/(?P<pk>\d+)/$', networkViewNumeric, name="individual-network-numeric"),
    url(r'^network/$', RedirectView.as_view(pattern_name="people_search", permanent=False)),
    url(r'^network/(?P<URL_for_detail>[\w\-\_\.]+)/$', NetworkView.as_view(), name="individual-network"),
    url(r'^edit/$',RedirectView.as_view(pattern_name="home", permanent=False)),
    url(r'^edit/(?P<pk>\d+)/$', PhD_EditView.as_view()),
    url(r'^detail/$', RedirectView.as_view(pattern_name="people_search", permanent=False)),
    url(r'^detail/(?P<pk>\d+)/$', PhD_numeric_detail_view, name="PhD-numeric-detail-view"),
    url(r'^detail/(?P<URL_for_detail>[\w\-\_\.]+)/$', PhDDetailView.as_view(), name="PhD-detail-view"),
    url(r'^$', HomePageView.as_view(), name="home"),
]
