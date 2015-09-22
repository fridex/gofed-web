from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class GoMail(models.Model):
	user            = models.ForeignKey(User)
	#
	notify_request  = models.BooleanField(default = False)
	notify_review   = models.BooleanField(default = False)

	class Meta:
		verbose_name = "Mail Notification"
		verbose_name_plural = "Mail Notifications"

	def __str__(self):
		return "GoMail " + self.user.username
		pass

	def clean(self):
		print self.user.email
		if self.notify_request or self.notify_review:
			if self.user.email is None or self.user.email == "":
				raise ValidationError('No e-mail found for user ' + self.user.username)

