from enum import Enum
import sys
import os
import shutil
from subprocess import Popen, PIPE
from goview.models import GoProjectLog, GoProjectDesc, GoProjectCommit, db_lock
from django.utils import timezone
import dateutil.parser
from dateutil.parser import parse as parse_date
from django.utils import timezone
from django.conf import settings
from django_cron import logger as cron_logger
import datetime
import urllib2
from django.core.exceptions import ObjectDoesNotExist

class SCMType(Enum):
	git       = 1
	mercurial = 2

class SCMException(Exception):
	pass

class SCMNotFound(SCMException):
	pass

class SCMErrorFirstCommit(SCMException):
	pass

def runCommand(cmd, cwd = "."):
	''' Run command `cmd' in working directory `cwd' '''
	process = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True, cwd=cwd, close_fds=True)
	stdout, stderr = process.communicate()
	rt = process.returncode
	if rt != 0:
		raise SCMException(stderr)
	return stdout, stderr, rt

def copytree(src, dst):
	''' Copy directory tree `src' to `dst', ignore broken symlinks '''
	try:
		shutil.copytree(src, dst, symlinks = True)
	except shutil.Error as e:
		print >> sys.stderr, ('Error: %s' % e)
		return False
	except OSError as e:
		print >> sys.stderr, ('Error: %s' % e)
		return False
	return True

class GoProjectSCMPool():
	def __init__(self, repo_file = None):
		self.projects = []

		if repo_file is not None:
			self.parse_repo_file(repo_file)

	def update_all(self, local = False):
		ret = 0
		for project in self.projects:
			try:
				project.update()
			except Exception as e:
				print >> sys.stderr, e.message
				cron_logger.error(e.message)
				ret = 1
		return ret

	def get_all(self):
		return self.projects

	def get_project(self, project_id):
		try:
			project_id_int = int(project_id)
		except ValueError:
			project_id_int = None

		for project in self.projects:
			if project.id == project_id_int or project.full_name == str(project_id):
				return project
		raise SCMNotFound()

	def get_list(self):
		res = []
		for project in self.projects:
			res.append({'full_name': project.full_name,
							'trend': project.trend,
							'scm_url': project.scm_url,
							'id': project.id})
		return res

	def add_project(self, name, full_name, scm_url):
		self.projects.append(GoProjectSCM(name, full_name, scm_url))

	def parse_repo_file(self, repo_file):
		f = open(repo_file, 'r')

		for line in f:
			content = line.split('\t')
			self.projects.append(GoProjectSCM(content[1], content[0], content[2][:-1]))

		f.close()

class GoProjectSCM():
	def __init__(self, name = None, full_name = None, scm_url = None):
		def update_repo_git():
			if os.path.isdir(self.repo_path):
				runCommand("git pull", self.repo_path)
			else:
				runCommand("git clone " + self.scm_url + " " + self.repo_path)

		def update_repo_hg():
			if os.path.isdir(self.repo_path):
				runCommand("hg pull", self.repo_path)
			else:
				runCommand("hg clone " + self.scm_url + " " + self.repo_path)

		def get_commit_id_git(tree):
			commit = runCommand("git rev-parse HEAD", tree)
			return commit[0][:-1]

		def get_commit_id_hg(tree):
			#commit = runCommand("hg --debug id -i", tree)
			commit = runCommand("hg id -i --debug", tree)
			return commit[0][:-1]

		def to_prev_commit_git(tree):
			try:
				runCommand("git reset --hard HEAD^", tree)
			except SCMException as ex:
				r = runCommand("git log --format=%H -n 1", tree)
				commit = r[0][:-1]
				if commit == get_commit_id_git(tree):
					raise SCMErrorFirstCommit()
				else:
					raise ex

		def to_prev_commit_hg(tree):
			r = runCommand("hg id --num", tree)
			commit = int(r[0][:-1])
			if commit == 0:
				raise SCMErrorFirstCommit()
			else:
				runCommand("hg update -r " + str(commit - 1) , tree)

		def get_commit_msg_git(tree):
			msg = runCommand("git log --format=%B -n 1", tree)
			msg = msg[0].split('\n')[0]
			return msg[:-1]

		def get_commit_msg_hg(tree):
			r = runCommand("hg id --num", tree)
			msg = runCommand('hg log --template "{desc|firstline}" -r %d' % int(r[0]), tree)
			return msg[0]

		def get_commit_author_git(tree):
			msg = runCommand("git log --format='%an <%ae>' -n 1", tree)
			msg = msg[0].split('\n')[0]
			return msg

		def get_commit_author_hg(tree):
			msg = runCommand("hg log --git -l 1", tree)
			msg = msg[0].split('\n')
			return msg[2][len("user:        "):-1]

		def get_commit_tag_git(tree):
			msg = runCommand("git tag --points-at HEAD", tree)
			msg = msg[0]
			return msg

		def get_commit_tag_hg(tree):
			msg = runCommand('hg log -r "." --template "{latesttag}\n"', tree)
			msg = msg[0]
			return msg

		def get_commit_date_git(tree):
			msg = runCommand("git log --format=%ad -n 1", tree)
			return parse_date(msg[0][:-1])

		def get_commit_date_hg(tree):
			r = runCommand("hg id --num", tree)
			ret = runCommand('hg log -r %d --template "{date|isodate}\n"' % int(r[0]), tree)
			return parse_date(ret[0])

		self.scm_url      = scm_url
		self.name         = name or full_name
		self.full_name    = full_name
		self.trend        = 0

		if not self.full_name:
			raise SCMException("No name nor full name specified!")

		self.__sync_db_desc()
		self.scm_type  = SCMType.git if self.scm_url.endswith(".git") else SCMType.mercurial
		self.data      = []
		self.repo_path = settings.REPO_PATH + self.full_name

		if self.scm_type == SCMType.git:
			self.__update_repo        = update_repo_git
			self.__get_commit_id      = get_commit_id_git
			self.__to_prev_commit     = to_prev_commit_git
			self.__get_commit_msg     = get_commit_msg_git
			self.__get_commit_author  = get_commit_author_git
			self.__get_commit_tag     = get_commit_tag_git
			self.__get_commit_date    = get_commit_date_git
		elif self.scm_type == SCMType.mercurial:
			self.__update_repo        = update_repo_hg
			self.__get_commit_id      = get_commit_id_hg
			self.__to_prev_commit     = to_prev_commit_hg
			self.__get_commit_msg     = get_commit_msg_hg
			self.__get_commit_author  = get_commit_author_hg
			self.__get_commit_tag     = get_commit_tag_hg
			self.__get_commit_date    = get_commit_date_hg
		else:
			raise Exception('Unknown scm type')

	def __str__(self):
		return self.full_name

	def __update_data(self, commit = None):
		def get_update_data(tmp_tree1, tmp_tree2, current_commit):
			ret = {}

			out = runCommand("gofed apidiff -av " + tmp_tree1 + " " + tmp_tree2)
			lines = out[0].split('\n')

			ret['commit']      = current_commit
			ret['commit_msg']  = self.__get_commit_msg(tmp_tree2)
			ret['date']        = self.__get_commit_date(tmp_tree2)
			ret['author']      = self.__get_commit_author(tmp_tree2)
			ret['tag']         = self.__get_commit_tag(tmp_tree2)
			ret['added']       = []
			ret['modified']    = []

			current_package = "#"
			for line in lines:
				if line.startswith("\t+"):
					ret['added'].append(line[len("\t+"):] + current_package)
				elif line.startswith("\t-"):
					ret['modified'].append(line[len("\t-"):] + current_package)
				elif line.startswith("Package: "):
					current_package = "#" + line[len("Package: "):]

			return ret

		SUFFIX1 = "_gofed-web1"
		SUFFIX2 = "_gofed-web2"

		apiGitStats = { "added": [], "modified": [], "commit": [], "trend": -1, "log": [] }

		tmp_tree1 = self.repo_path + SUFFIX1
		tmp_tree2 = self.repo_path + SUFFIX2

		shutil.rmtree(tmp_tree1, ignore_errors = True)
		shutil.rmtree(tmp_tree2, ignore_errors = True)

		# Make working copies
		if copytree(self.repo_path, tmp_tree1) == False or copytree(self.repo_path, tmp_tree2) == False:
			raise Exception('Failed to copy working trees')

		updates = []
		while True:
			current_commit = self.__get_commit_id(tmp_tree2)
			if current_commit == commit:
				break

			try:
				self.__to_prev_commit(tmp_tree1)
			except SCMErrorFirstCommit:
				break
			updates.append(get_update_data(tmp_tree1, tmp_tree2, current_commit))
			self.__to_prev_commit(tmp_tree2)

		shutil.rmtree(tmp_tree1, ignore_errors=True)
		shutil.rmtree(tmp_tree2, ignore_errors=True)

		return list(reversed(updates))

	def __sync_db_desc(self):
		q = GoProjectDesc.objects.filter(full_name__exact=self.full_name).only('pk')
		if not q:
			project_Desc              = GoProjectDesc()
			project_Desc.name         = self.name
			project_Desc.full_name    = self.full_name
			project_Desc.scm_url      = self.scm_url
			project_Desc.trend        = 0
			project_Desc.update_date  = None
			project_Desc.save()
			self.id                   = project_Desc.pk
		else:
			self.name                 = q[0].name
			self.full_name            = q[0].full_name
			self.scm_url              = q[0].scm_url
			self.trend                = q[0].trend
			self.update_date          = q[0].update_date
			self.id                   = q[0].pk

	def get_info(self):
		return {'full_name': self.full_name,
					'name': self.name,
					'id': self.id,
					'update': self.update_date,
					'trend': self.trend,
					'scm_url': self.scm_url}

	def get_dependnency_graph(self):
		with open(self.repo_path + '/graph.png', "rb") as f:
			image = f.read()
		return image

	def update(self, local = False):
		def calculate_trend():
			commits = GoProjectCommit.objects.filter(project_desc__id=self.id).order_by('-id')[:20]

			trend = 0
			weight = 20
			for c in commits:
				trend += c.changes_count * weight
				weight -= 1

			return trend

		project_Desc = None
		commit = None

		with db_lock([GoProjectLog, GoProjectCommit, GoProjectDesc]):
			print >> sys.stderr, "Updating " + self.full_name
			commit_q = GoProjectCommit.objects.filter(project_desc_id=self.id).order_by('-id').only('commit')
			if commit_q:
				commit = commit_q[0].commit

			if not local:
				self.__update_repo()

			updates = self.__update_data(commit)

			for rec in updates:
				project_commit = GoProjectCommit()
				project_commit.project_desc_id = self.id
				project_commit.commit = rec['commit']
				project_commit.commit_msg = rec['commit_msg']
				project_commit.author = rec['author']
				project_commit.date = rec['date']
				project_commit.tag = rec['tag']
				project_commit.changes_count = len(rec['added']) + len(rec['modified'])
				project_commit.save()

				for a in rec['added']:
					project_log                 = GoProjectLog()
					project_log.project_commit  = project_commit
					project_log.modification    = False
					change, package             = a.split('#')
					project_log.api_change      = change
					project_log.package_name    = package
					project_log.save()

				for m in rec['modified']:
					project_log                 = GoProjectLog()
					project_log.project_commit  = project_commit
					project_log.modification    = True
					change, package             = m.split('#')
					project_log.api_change      = change
					project_log.package_name    = package
					project_log.save()

		if updates:
			runCommand("gofed scan-deps -g", self.repo_path)

		q = GoProjectDesc.objects.filter(full_name__exact=self.full_name).get()
		q.update_date = timezone.now()
		q.trend = calculate_trend()
		q.save()

	def __obj2dict(self, obj):
		ret = {}
		ret['commit']      = obj.commit
		ret['commit_msg']  = obj.commit_msg
		ret['author']      = obj.author
		ret['tag']         = obj.tag
		ret['date']        = str(obj.date)
		ret['added']       = []
		ret['modified']    = []

		if int(obj.changes_count) != 0:
			logs = GoProjectLog.objects.filter(project_commit_id=obj.pk)
			for l in logs:
				i = {}
				i['change'] = str(l.api_change)
				i['package'] = str(l.package_name)

				if l.modification:
					ret['modified'].append(i)
				else:
					ret['added'].append(i)

		return ret

	def fetch_commit(self, commit1, commit2):
		if commit2 == None or len(commit2) == 0:
			fetch = True
			commit_start = None
		else:
			fetch = False
			commit_start = commit1

		commit_end = commit2 if commit2 else commit1
		commits = GoProjectCommit.objects.filter(project_desc_id=self.id).order_by('-id')

		i = 0
		ret = []
		for c in commits:
			if not fetch and str(c.commit).startswith(commit_end):
				commit_start, commit_end = commit_end, commit_start

			if not fetch and str(c.commit).startswith(commit_start):
				fetch = True

			if fetch:
				i += 1
				ret.append(self.__obj2dict(c))

			if str(c.commit).startswith(commit_end) or i >= settings.MAX_REPLY_COUNT:
				return ret

		return []

	def fetch_depth(self, depth, from_commit):
		fetch = from_commit == None or len(from_commit) == 0
		commits = GoProjectCommit.objects.filter(project_desc__id=self.id).order_by('-id')

		depth = int(depth)

		if depth > settings.MAX_REPLY_COUNT:
			depth = settings.MAX_REPLY_COUNT

		i = 0
		ret = []
		for c in commits:
			if not fetch and str(c.commit).startswith(from_commit):
				fetch = True

			if fetch:
				i += 1
				ret.append(self.__obj2dict(c))

			if i == depth:
				break

		return ret

	def fetch_date(self, date1, date2):
		commits = GoProjectCommit.objects.filter(project_desc_id=self.id).order_by('-id')

		try:
			date1 = dateutil.parser.parse(date1)
		except ValueError:
			return {'error': date1}

		if date2 and len(date2) > 0:
			try:
				date2 = dateutil.parser.parse(date2)
			except ValueError:
				return {'error': date2}
		else:
			date2 = datetime.datetime.now()

		if date1 < date2:
			date1, date2 = date2, date1

		ret = []
		date1 = timezone.make_aware(date1, timezone.get_default_timezone())
		date2 = timezone.make_aware(date2, timezone.get_default_timezone())

		i = 0
		fetch = False
		for c in commits:
			if not fetch and c.date <= date1:
				fetch = True

			if c.date <= date2 or i > settings.MAX_REPLY_COUNT:
				break

			if fetch:
				i += 1
				ret.append(self.__obj2dict(c))

		return ret

	def check_deps(self, commit):
		try:
			response = urllib2.urlopen("http://pkgs.fedoraproject.org/cgit/%s.git/plain/%s.spec" %
													(self.full_name, self.full_name))
			ret = response.read()
		except urllib2.HTTPError as e:
			return {"error": "Fedora DB: " + str(e)}
		ret = ret.split('\n')

		commit_fedora = None
		for line in ret:
			if line.startswith("%global commit"):
				commit_fedora = line.split()[-1]

		if not commit_fedora:
			return {"error": "Fedora commit not found in spec"}

		try:
			commit_fedora = GoProjectCommit.objects.filter(project_desc__full_name = self.full_name,
																			commit__startswith = commit_fedora).get()
		except ObjectDoesNotExist:
			return {"error": "Fedora commit not found in DB"}

		try:
			commit_db = GoProjectCommit.objects.filter(project_desc__full_name = self.full_name,
																		commit__startswith = commit).get()
		except ObjectDoesNotExist:
			return {"error": "Requested commit not found in DB"}

		if commit_fedora.id > commit_db.id:
			return {"status": "newer"}
		elif commit_fedora.id < commit_db.id:
			return {"status": "older"}
		else:
			return {"status": "up2date"}

