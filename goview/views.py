from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from goview.form import GoReviewForm, GoRequestForm
from django.http import HttpResponseRedirect
import json
from goview.project import GoProjectSCMPool, GoProjectSCM
import sys
from goview.models import GoProjectReview, GoProjectRequest, GoPage
from goview.graph import GoGraph
from datetime import datetime
from gomail.mailer import notify_review, notify_request
from django.db import InternalError
from django.conf import settings

# Base HTML views

def index(request):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	return render(request, 'goview/list_projects.html', {'projects': pool.get_all()})

def project(request, project_id):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	project = pool.get_project(project_id)
	if project.update_date:
		project.update_date = project.update_date.strftime('%F %T %z')
	return render(request, 'goview/project.html', {'project': project})

# Commands

def update(request, project_id):
	if request.user.is_authenticated():
		pool = GoProjectSCMPool(settings.GOLANG_REPOS)
		pool.get_project(project_id).update()
		return HttpResponse("OK", content_type="text/plain")
	else:
		return HttpResponseForbidden()

def update_all(request):
	if request.user.is_authenticated():
		pool = GoProjectSCMPool(settings.GOLANG_REPOS)
		p = pool.update_all()
		return HttpResponse("OK", content_type="text/plain")
	else:
		return HttpResponseForbidden()

# REST service

def rest_list(request):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	res = pool.get_list()
	return HttpResponse(json.dumps(res), content_type='application/json')

def rest_info(request, project_id):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	res = pool.get_info(project_id)
	# datetime is not serializable for JSON
	res['update'] = res['update'].strftime('%F %T %z') if res['update'] is not None else None
	return HttpResponse(json.dumps(res), content_type='application/json')

def rest_commit(request, project_id, commit1, commit2 = None):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	res = pool.fetch_commit(project_id, commit1, commit2)
	return HttpResponse(json.dumps(res), content_type='application/json')

def rest_depth(request, project_id, depth, from_commit = None):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	res = pool.fetch_depth(project_id, depth, from_commit)
	return HttpResponse(json.dumps(res), content_type='application/json')

def rest_date(request, project_id, date1, date2 = None):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	res = pool.fetch_date(project_id, date1, date2)
	return HttpResponse(json.dumps(res), content_type='application/json')

def rest_check_deps(request, project_id, commit):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	res = pool.check_deps(project_id, commit)
	return HttpResponse(json.dumps(res), content_type='application/json')

# Graph service

def makeSVG(name, data, type):
	if type == 'a' or type == 'added':
		res = GoGraph.makeSVGAdded(name, data)
	elif type == 'm' or type == 'modified':
		res = GoGraph.makeSVGRemoved(name, data)
	elif type == 't' or type == 'total' or type == None or len(type) == 0:
		res = GoGraph.makeSVGTotal(name, data)
	elif type == 'c' or type == 'cpc':
		res = GoGraph.makeSVGCPC(name, data)
	else:
		raise InternalError("unsupported Graph type")
	return res

def graph_commit(request, project_id, commit1, commit2 = None, type = None):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	com = pool.fetch_commit(project_id, commit1, commit2)
	com.reverse()
	return HttpResponse(makeSVG(pool.get_project(project_id).full_name, com, type), content_type='image/svg+xml')

def graph_depth(request, project_id, depth, from_commit = None, type = None):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	com = pool.fetch_depth(project_id, depth, from_commit)
	com.reverse()
	return HttpResponse(makeSVG(pool.get_project(project_id).full_name, com, type), content_type='image/svg+xml')

def graph_date(request, project_id, date1, date2 = None, type = None):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	com = pool.fetch_date(project_id, date1, date2)
	com.reverse()
	return HttpResponse(makeSVG(pool.get_project(project_id).full_name, com, type), content_type='image/svg+xml')

def graph_dependency(request, project_id):
	pool = GoProjectSCMPool(settings.GOLANG_REPOS)
	return HttpResponse(pool.get_dependnency_graph(project_id), content_type='image/png')

# Requests & Reviews

def request(request):
	if request.method == 'POST':
		form = GoRequestForm(request.POST)
		if form.is_valid():
			go_request = GoProjectReview()
			go_request.email = request.POST['email']
			go_request.text = request.POST['text']
			go_request.scm_url = request.POST['scm_url']
			go_request.date = datetime.now()
			go_request.save()
			notify_request(go_request)
			return HttpResponseRedirect('/request-added')
	else:
		form = GoRequestForm()
	rev = GoPage.objects.get(url_name__exact='request')
	return render(request, 'goview/request.html', {'page': rev, 'form': form})

def review(request):
	if request.method == 'POST':
		form = GoReviewForm(request.POST)
		if form.is_valid():
			go_review = GoProjectReview()
			go_review.email = request.POST['email']
			go_review.text = request.POST['text']
			go_review.date = datetime.now()
			go_review.save()
			notify_review(go_review)
			return HttpResponseRedirect('/review-added')
	else:
		form = GoReviewForm()
	rev = GoPage.objects.get(url_name__exact='review')
	return render(request, 'goview/review.html', {'page': rev, 'form': form})

# Generic pages

def page(request, page_name):
	page = get_object_or_404(GoPage, url_name__exact=page_name)
	return render(request, 'goview/page.html', {'page': page})

