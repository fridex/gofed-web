from gomail.models import GoMail
from goview.models import GoProjectRequest
from goview.models import GoProjectReview
from smtplib import SMTPRecipientsRefused

import sys
from django.contrib.auth.models import User

def notify_review(review):
	users = GoMail.objects.filter(notify_review = True)
	for gouser in users:
		try:
			gouser.user.email_user("[goweb-review] A new review was added",
					'Text:\n\n\t' + review.text)
		except SMTPRecipientsRefused:
			pass

def notify_request(request):
	users = GoMail.objects.filter(notify_request = True)
	for gouser in users:
		try:
			gouser.user.email_user("[goweb-request] A new request was added",
					'SCM URL: ' + request.scm_url + '\nText:\n\n\t' + request.text)
		except SMTPRecipientsRefused:
			pass

