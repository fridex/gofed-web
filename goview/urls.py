from django.conf.urls import patterns, url
from django.contrib import admin
from django.conf.urls import include

from goview import views

urlpatterns = patterns('',
	# Admin
	url(r'^admin/?', include(admin.site.urls)),
	# Base HTML views
	url(r'^$', views.index, name='index'),
	url(r'^(?P<project_id>[0-9]+)/?$', views.project, name='project'),
	url(r'^project/(?P<project_id>[a-zA-Z_\-0-9]+)/?$', views.project, name='project'),
  # Commands
	url(r'^update/(?P<project_id>[a-zA-Z_\-0-9]+)/?$', views.update, name='update'),
	url(r'^update/?$', views.update_all, name='update_all'),
	# Graph service
	url(r'^graph/?(?P<type>([amtc]|(added)|(modified)|(total)|(cpc)))?/commit/(?P<project_id>[a-zA-Z_\-0-9]+)/(?P<commit1>[0-9a-z]{4,40})(?:/(?P<commit2>[0-9a-z]{4,40}))?/graph.svg$', views.graph_commit, name='graph_commit'),
	url(r'^graph/?(?P<type>([amtc]|(added)|(modified)|(total)|(cpc)))?/depth/(?P<project_id>[a-zA-Z_\-0-9]+)/(?P<depth>[0-9]+)(?:/(?P<from_commit>[0-9a-z]{4,40}))?/graph.svg$', views.graph_depth, name='graph_depth'),
	url(r'^graph/?(?P<type>([amtc]|(added)|(modified)|(total)|(cpc)))?/date/(?P<project_id>[a-zA-Z_\-0-9]+)/(?P<date1>[0-9\-]+)(?:/(?P<date2>[0-9\-]+)?)/graph.svg$', views.graph_date, name='graph_date'),
	url(r'^graph/dependency/(?P<project_id>[a-zA-Z_\-0-9]+)/graph.png$', views.graph_dependency, name='graph_dependency'),
	# REST service
	url(r'^rest/list/$', views.rest_list, name='rest_list'),
	url(r'^rest/info/(?P<project_id>[a-zA-Z_\-0-9]+)/$', views.rest_info, name='rest_info'),
	url(r'^rest/commit/(?P<project_id>[a-zA-Z_\-0-9]+)/(?P<commit1>[0-9a-z]{4,40})(?:/(?P<commit2>[0-9a-z]{4,40}))?/?$', views.rest_commit, name='rest_commit'),
	url(r'^rest/depth/(?P<project_id>[a-zA-Z_\-0-9]+)/(?P<depth>[0-9]+)(?:/(?P<from_commit>[0-9a-z]{4,40}))?/?$', views.rest_depth, name='rest_depth'),
	url(r'^rest/date/(?P<project_id>[a-zA-Z_\-0-9]+)/(?P<date1>[0-9\-]+)(?:/?P<date2>[0-9\-]*)?/?$', views.rest_date, name='rest_date'),
	# Review & Request
	url(r'^review/?$', views.review, name='review'),
	url(r'^request/?$', views.request, name='request'),
	# Generic pages
	url(r'^(?P<page_name>[a-z\-0-9]+)/?$', views.page, name='page'),
)
