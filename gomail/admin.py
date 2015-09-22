from django.contrib import admin
from gomail.models import GoMail

class GoMailAdmin(admin.ModelAdmin):
	fieldsets = [
		('User notification management', {'fields': ['user', 'notify_request', 'notify_review']}),
	]
	list_display = ('user', 'notify_request', 'notify_review')
	list_filter = ['notify_request', 'notify_review']

admin.site.register(GoMail, GoMailAdmin)

