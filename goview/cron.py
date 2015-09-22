# -*- coding: utf-8 -*-
from django_cron import CronJobBase, Schedule
from django.conf import settings
from goview.project import GoProjectSCMPool

class UpdateCronJob(CronJobBase):
	RUN_EVERY_MINS = 180

	schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
	code = 'goview.update_cron_job'    # a unique code

	def do(self):
		pool = GoProjectSCMPool(settings.GOLANG_REPOS)
		ret = pool.update_all()
		return ret
