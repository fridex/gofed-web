import contextlib
import sys
from django.db import models, connection
from django.utils import formats

class GoProjectReview(models.Model):
	#
	email          = models.CharField(max_length = 200)
	text           = models.TextField()
	date           = models.DateTimeField()
	notes          = models.TextField()
	resolved       = models.BooleanField(default = False)

	class Meta:
		verbose_name = "Go Project Review"
		verbose_name_plural = "Go Project Reviews"

	def __unicode__(self):
		return "{0} - {1}".format(
				formats.date_format(self.date, "SHORT_DATETIME_FORMAT"),
				self.email)

class GoProjectRequest(models.Model):
	#
	email          = models.CharField(max_length = 200)
	scm_url        = models.CharField(max_length = 250)
	text           = models.TextField()
	date           = models.DateTimeField()
	notes          = models.TextField()
	resolved       = models.BooleanField(default = False)

	class Meta:
		verbose_name = "Go Project Request"
		verbose_name_plural = "Go Project Requests"

	def __unicode__(self):
		return self.scm_url

class GoPage(models.Model):
	#
	url_name       = models.CharField(max_length = 250, unique = True)
	name           = models.CharField(max_length = 250)
	content        = models.TextField()

	class Meta:
		verbose_name = "Page"
		verbose_name_plural = "Pages"

	def __unicode__(self):
		return self.name

class GoProjectDesc(models.Model):
	#
	name           = models.CharField(max_length = 250)
	full_name      = models.CharField(max_length = 250, unique = True)
	scm_url        = models.CharField(max_length = 250)
	trend          = models.IntegerField(default = 0)
	update_lock    = models.BooleanField(default = False)
	update_date    = models.DateTimeField(null = True)

	class Meta:
		verbose_name = "Go Project Description"
		verbose_name_plural = "Go Project Descriptions"

	def __unicode__(self):
		return self.full_name

class GoProjectCommit(models.Model):
	project_desc   = models.ForeignKey(GoProjectDesc)
	#
	commit         = models.CharField(max_length = 250)
	tag            = models.CharField(max_length = 250)
	commit_msg     = models.TextField()
	author         = models.CharField(max_length = 250)
	date           = models.DateTimeField()
	changes_count  = models.IntegerField(default = 0)

	class Meta:
		verbose_name = "Go Project Commit"
		verbose_name_plural = "Go Project Commits"

	def __unicode__(self):
		return self.commit[:8]

class GoProjectLog(models.Model):
	project_commit = models.ForeignKey(GoProjectCommit)
	#
	modification   = models.BooleanField(default = False)
	api_change     = models.CharField(max_length = 250)
	package_name   = models.CharField(max_length = 250)

	class Meta:
		verbose_name = "Go Project Log"
		verbose_name_plural = "Go Project Logs"

	def __unicode__(self):
		return "{0}/{1}".format(self.package_name, self.api_change)

@contextlib.contextmanager
def db_lock(tables):
	def lock_tables(tables):
		table_names = [model._meta.db_table for model in tables]
		statement = ', '.join(['%s WRITE' % table for table in table_names])
		statement = 'LOCK TABLES %s' % ', '.join([statement])
		cursor = connection.cursor()
		print >> sys.stderr, "Locking..."
		#cursor.execute(statement)
		return cursor

	if connection.settings_dict['ENGINE'] != 'django.db.backends.mysql':
		raise Exception("Database lock is probably not supported!")

	cursor = lock_tables(tables)
	try:
		yield cursor
	finally:
		print >> sys.stderr, "Unlocking..."
		cursor.execute("UNLOCK TABLES")
