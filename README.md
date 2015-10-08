# gofed-web

A gofed web service for analysing and visualising Golang projects.
See also https://github.com/ingvagabund/gofed

This application is deployed at http://209.132.179.123/

## Requirements
* gofed - https://github.com/ingvagabund/gofed
  ```
# yum install gofed
  ```
* pygal library - http://pygal.org/
  ```
# yum install python-pygal
  ```
* MySQL - http://www.mysql.com/
  ```
# yum install mysql
# yum install MySQL-python
  ```
* Django-cron - http://django-cron.readthedocs.org/
```
# pip install django_cron
```
* Django
```
# pip install Django==1.7.9
```
* dateutils
```
# pip install python-dateutil
```
* django-debug-toolbar
```
# pip install django-debug-toolbar
```

The application can be run on any database supported by Django, but there can be
required database locking (e.g. when updating a project), which is not supported
by all databases. Currently, gofed-web fully supports only MySQL database.

Optionally for a production deployment:
  ```
# yum install uglify-js
  ```

### Database Setup

```
CREATE DATABASE goweb;
CREATE USER 'goweb'@'localhost' IDENTIFIED BY 'yoursecretpassword';
GRANT ALL ON goweb.* TO 'goweb'@'localhost';
ALTER DATABASE goweb CHARACTER SET utf8 COLLATE utf8_unicode_ci;
```

### Apache Configuration

```
<VirtualHost *:80>
	ServerAdmin your@mail
	ServerName localhost
	ServerAlias localhost

	DocumentRoot /var/www/goweb/

	<Directory /var/www/goweb/>
		Order allow,deny
		Allow from all
	</Directory>

	WSGIScriptAlias / /var/www/goweb/wsgi.py
	WSGIDaemonProcess localhost python-path=/var/www/goweb/:/home/env/lib/python2.7/site-packages user=apache
	WSGIProcessGroup localhost

	Alias /static/ /var/www/goweb/static/
	<Location "/static/">
		Options -Indexes
	</Location>

	ErrorLog /var/log/httpd/goweb_error.log
</VirtualHost>
```

### SELinux
```
# chcon -R -t httpd_sys_script_rw_t cache/
# chcon -R -t httpd_sys_script_exec_t <PATH_TO_GOFED_BIN>
# chcon -R -t httpd_sys_script_ro_t golang.repos
```

## Running the Server

For non-production environments, you can use Django's web-server:
  ```
$ python manage.py runserver 8080
  ```
This will run the server on port 8080, so you can access it via
http://localhost:8080/

For a production environment, please follow Django's tutorial:

https://docs.djangoproject.com/en/1.6/howto/deployment/

If you wish to be periodically synced, register scheduled updates. Place the
following into your /etc/cron.hourly:

```
#!/bin/bash

CRONLOG="/var/www/goweb/cron.log"

date >> ${CRONLOG}
python /var/www/goweb/manage.py runcrons >> ${CRONLOG} 2>&
```

Updates are run every 3 hours. If you want to adjust update frequency,
modify `goview/cron.py`. To run update manually, just fire
```
python manage.py runcrons "goview.cron.UpdateCronJob
```

## Documentation

This application was designed mainly as a query service, but it can be used even
as a web client for visualising results.

See `gofed client` to query service from command line:
https://github.com/ingvagabund/gofed

### Presentation Service

The server provides a web client written in HTML/jQuery. This service can be
easily accessed on configured web port. It visualizes JSON responses from the
server.

### REST Service

The server provides a simple REST service for quering. It can be accessed via
`/rest/`.

##### REST Service Syntax:

```
/rest/COMMAND/ARG1/ARG2/ARG3/
```

##### Available Commands:

* `list` - list of all projects
* `info` - basic info for a project
* `commit` - list of changes for a project between provided commits
* `depth` - list of changes for a project depending on provided depth
* `date` - list of changes for a project between dates
* `check-deps` - check whether commit ARG2 is newer then in the one in Fedora

| Command       | ARG1          | ARG2          | ARG3          |
|---------------|---------------|---------------|---------------|
| `list`        |     -         |     -         |     -         |
| `info`        | project id    |     -         |     -         |
| `commit`      | project id    | from commit   | to commit     |
| `depth`       | project id    | depth         | from commit   |
| `date`        | project id    | from date     | to date       |
| `check-deps`  | project id    | commit        |     -         |

<a name="command_notes"></a>
* `project id` can be full name of a project or numerical id listed in `list` or
  `info` command but it is *highly recommended* to use a full name of a project,
  since numerical id can be changed
* `ARG3` can be always omitted; if so, it defaults to the most recent commit
* commit SHAs have to be at least 4 digits long
* don't worry about ARG2 and ARG3 positioning; if you accidently swap them, the
  server will intelligently swap them back
* date format is YYYY-MM-DD (e.g. 2015-07-22)

##### Response Data and Examples

The server will respond with JSON. List of provided data in a response:

* `list`
  * example query: ```/rest/list/```
  * example response:
  ```[{"trend": 18, "scm_url": "https://bitbucket.org/kardianos/osext", "full_name": "golang-bitbucket-kardianos-osext", "id": 1}, {"trend": 19, "scm_url": "https://github.com/howeyc/gopass.git", "full_name": "golang-github-howeyc-gopass", "id": 2}]```
* `info`
  * example query: ```/rest/info/golang-github-howeyc-gopass/```
  * example response: ```{"name": "osext", "trend": 18, "update": "2015-07-16 09:36:20 +0000", "scm_url": "https://bitbucket.org/kardianos/osext", "full_name": "golang-bitbucket-kardianos-osext", "id": 1}```
* `commit`
  * example query: ```/rest/commit/golang-github-howeyc-gopass/2c70fa7/1af4cd0/```
  * example response: ```[{"added": [], "author": "Chris Howey <chris@howey.me>", "modified": [], "date": "2015-02-07 20:50:41+00:00", "commit": "2c70fa70727c953c51695f800f25d6b44abb368e", "commit_msg": "Fix issue where some how NUL (0 byte) is returned from getch on windows"}, {"added": [], "author": "Chris Howey <chris@howey.me>", "modified": [], "date": "2014-12-11 00:50:38+00:00", "commit": "1af4cd08f75465cbb0fcec37b64b77c4a6b6d41a", "commit_msg": "Fix issue #10. Possible that number of bytes read is trash"}]```
* `depth`
  * example query: ```/rest/depth/golang-github-howeyc-gopass/3/1af4cd0/```
  * example response: *same as for `commit`, but for the specified depth*
* `date`
  * example query: ```/rest/date/golang-github-howeyc-gopass/2015-06-22/2015-07-22/```
  * example response: *same as for `commit`, but for the specified date frame*

### Graph Service

You can retrieve an SVG image to visualise dependencies, changes and
modifications within a project.

##### Graph Service Syntax:

```
/graph/[TYPE/]COMMAND/ARG1/ARG2/ARG3/graph.svg
```

##### Available Commands and Types:

There are currently four types of graphs:
* `added` or `a` - visualise additions in a project
* `modified` or `m` - visualise modifications in a project
* `total` or `t` - visualise additions and modifications in a project
* `cpc` or `c` - visualise changes per commit in a 10 commit-frame

Commands are designed to follow REST service semantic and syntax:
* `commit` - visualise changes for a project between provided commits
* `depth` - visualise changes for a project depending on provided depth
* `date` - visualise changes for a project between dates

| Command   | ARG1          | ARG2          | ARG3          |
|-----------|---------------|---------------|---------------|
| `commit`  | project id    | from commit   | to commit     |
| `depth`   | project id    | depth         | from commit   |
| `date`    | project id    | from date     | to date       |

See [command notes for REST](#command notes) for more info.

##### Visualising Dependencies

The server also provides a query for visualising project dependencies. To use
it, simply access `/graph/dependency/<PROJECT_ID>/graph.png`. As you can see,
the PNG image format is used.

### Updates

The server is configured to update database once a day. It is recommended to
keep database up-to-date if you wish to be synchronized.

If you are an authorized user, you can force an update. Please note that this
process takes some time (and it takes a lot of time for very active projects) so
be patient. To keep consistent state of the database, database locks are used.
Not all databases supported by Django framework provide locks, gofed-web
currently supports only MySQL database locking.

### wanna help or a bug?

If you have found some weird behaviour and you are considering it as a bug, feel
free to contact me or send a pull request with a patch.

