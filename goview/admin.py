from django.contrib import admin
from django import forms
from goview.models import GoProjectRequest, GoProjectReview, GoPage
from goview.models import GoProjectDesc, GoProjectCommit, GoProjectLog

class GoProjectRequestAdmin(admin.ModelAdmin):
	fieldsets = [
		('Project request', {'fields': ['email', 'scm_url', 'date', 'resolved']}),
		('Text', {'fields': ['text']}),
		('Notes', {'fields': ['notes']}),
	]
	list_display = ('__str__', 'date', 'resolved')
	list_filter = ['resolved', 'date']
	search_fields = ['email', 'text', 'notes', 'scm_url']

admin.site.register(GoProjectRequest, GoProjectRequestAdmin)


class GoProjectReviewAdmin(admin.ModelAdmin):
	fieldsets = [
		('Project review', {'fields': ['email', 'date', 'resolved']}),
		('Text', {'fields': ['text']}),
		('Notes', {'fields': ['notes']}),
	]
	list_display = ('__str__', 'date', 'resolved')
	list_filter = ['resolved', 'date']
	search_fields = ['email', 'text', 'notes']

admin.site.register(GoProjectReview, GoProjectReviewAdmin)

class ContentModelForm(forms.ModelForm):
	content = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = GoPage
		fields = '__all__'

class GoPageAdmin(admin.ModelAdmin):
	form = ContentModelForm
	fieldsets = [
			('Page', {'fields': ['name', 'url_name', 'content']})
	]
	list_display = ['__str__']
	list_filter = []
	search_fields = ['name']

admin.site.register(GoPage, GoPageAdmin);

admin.site.register(GoProjectDesc)
admin.site.register(GoProjectCommit)
admin.site.register(GoProjectLog)
