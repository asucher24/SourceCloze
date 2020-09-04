(CI available only for gitlab)
[![pipeline status](https://gitlab.rlp.net/xxxx/SourceCloze/badges/master/pipeline.svg)](https://gitlab.rlp.net/xxxx/SourceCloze/-/commits/master)
[![coverage report](https://gitlab.rlp.net/xxxx/SourceCloze/badges/master/coverage.svg)](https://gitlab.rlp.net/xxxx/SourceCloze/-/commits/master)

# Source Cloze - Documentation of file structure

Source Cloze is an audience response system (ARS) for polls in form of cloze text from source code.
The application consists of a Django web application. Additionally an Add-In can be added to Office PowerPoint. But this was not tested in version 2.
The Add-In (Source Cloze Office) allows to create the poll.
The web application (Source Cloze) has the whole functionalities: The poll creation/ editing/resolution and allows the participation.

Demo for Source Cloze Office is available on https://sourcecloze.zdv.uni-mainz.de . 

This short documentation is only about the file structure and the content of important files.
For further information see:
- user documentation: Read assets/plugins/poll_creation/src/doc.html or visit application, login and open 'help' button
- developer documentation: Visit: https://sourcecloze.zdv.uni-mainz.de/admin/doc ('The code is the doc' ;-) )

## Developer
Josuar Glodde (2019)  
Anna Sucher (2020)  

## Quick Install
> Tested only with Debian 10 Server.
* Download this repository into /home/.../
* Change into repository with `cd /home/.../SourceCloze`
* Update file config/.env (at least the secret_key)
* Run the install script `./installForProduction.sh`
* Open browser and call https://<yourhostname>/

## Log files
The log file of the application can be found in `/var/log/apache2/sourcecloze_error.log`

## Source Cloze
Source Cloze is a standalone Django application. 
It allows an authenticated user (authenticated through https://gitlab.rlp.net) to create polls and view the results.
User which know the poll id can participate in the poll.  
In the following, all parts that have been part of the development are briefly explained.

### Settings

```
  .
  +-- conf
  |   +-- .env
  +-- sourcecloze
  |   +-- settings.py
  |   +-- settings_base.py
  |   +-- settings_logging.py
  |   +-- settings_test.py
  |   +-- urls.py
  |   +-- wsgi.py
  +-- manage.py
  +-- installForProduction.sh
  +-- apache.sourcecloze.conf 
  +-- requirements.txt
```

- Main django script: manage.py
- Django project settings in settings.py and settings_*.py (Core settings in settings_base)
- URL configuration in urls.py
- Deployment setup for uwsgi in wsgi.py
- Script for automatic production deployment on debian 10 with apache2: installForProduction.sh  
  Install everything in requirements.txt and patches apache.sourcecloze.conf with project path.  
  Configure apache2 settings (with apache.sourcecloze.conf).

### Authentication App

Allows users to authenticate with gitlab.rlp.net account.

```
	.
	+-- authentication
	|   +-- login.html
	|   +-- settings_authentication.py
	|   +-- views.py
	|   +-- urls.py
```

- UnitTests in tests.py
- Settings in settings_authentication.py
- login.html: Template for Login


### Pages App

Allows users to participate in a poll and fill in the clozes.

```
	.
	+-- pages
	|   +-- apps.py
	|   +-- tests.py
	|   +-- views.py
	|   +-- urls.py
```

- Setup in apps.py
- UnitTests in tests.py
- HTTP request and HTTP response handling in views.py

### Poll-API App

For managing the poll and communicating with the add-in/plug-ins.

```
	.
	+-- poll_api
	|   +-- migrations
	|   |   +-- 0001_initial.py
	|   +-- admin.py
	|   +-- apps.py
	|   +-- models.py
	|   +-- tests.py
	|   +-- utils.py
	|   +-- views.py
```

- Database migration in 0001_initial.py
- Register database for dministration tool in admin.py
- Setup in apps.py
- Database definition in models.py
- UnitTests in tests.py
- HTTP request and HTTP response handling in views.py


### Utils Folder 

Contains scripts used by the apps. Logik functions. E.g. merging poll answers.

```
	.
	+-- utils
	|   +-- DockerData.py
	|   +-- syntaxcheck.py
	|   +-- utils.py
	|   +-- utils_authentication.py
	|   +-- utils_pages.py
	|   +-- utils_poll_api.py
```
- DockerData: Init the docker containers and volumes
- syntaxcheck: Builds sourcecode from cloze and answers; created file and run compiler/interpreter to check the syntax
- utils: generel helpers e.g. custom exceptions
- utils_authentication: helper functions related to authentication
- utils_pages: Tools and database related methods in context of pages app
- utils_poll_api: Tools and database related methods in context of poll_api app

### Templates

```
  .
  +-- assets
  |   +-- templates
  |   |   +-- base.html
  |   |   +-- home.html
  |   |   +-- polloverview.html
  |   |   +-- status.html
  |   |   +-- vote.html
```

- home, polloverview, status and vote templates extends base template
- home: shows the participant view
- polloverview: Shows a list of self created polls
- status: shows the result page after participation
- vote: Shows the participation view
- All templates use static files

### Static Files

```
  .
  +-- assets
  |   +-- static
  |   |   +-- source-cloze-logo.png
  |   |   +-- source-cloze-logo-pen.png
  |   |   +-- styles.css
  |   |   +-- js
  |   |   |   +-- jquery-3.4.1.min.js
  |   |   |   +-- main.js
  |   |   +-- prism
  |   |   |   +-- prism.js
  |   |   |   +-- prism.css
```

- Stores icons (source-cloze-logo and favicon)
- style: css styles for templates
- js/main.js: Javascript for templates
- used libraries (jQuery, Prism), Must be served as static files

## Plug-Ins
Webapplication allows to use capsulated plugins. Its important to call them through a url route defined in any <DjangoApp>/urls.py and <DjangoApp>/views.py  
The application only uses the plugin: poll_creation.  
The 'source-cloze-office' is used to be added as an add-in to a powerpoint office client. But we recommand to use the web view (poll_creation). The office add-in is more like an artefact !

```
	.
	+-- assets
	|   +-- plugins
	|   |   +-- poll_creation/
	|   |   +-- source-cloze-office/
```
### Poll-Creation
#### General

Actually it is a static html file (index.html) with a lot of javascript inside js/ and styled with css defined in css/
Additionally there is a doc.html which contains the userdocumentation.
```
	.
	+-- assets
	|   +-- plugins
	|   |   +-- poll_creation
	|   |   |   +-- pub
	|   |   |   +-- src
	|   |   |   |   +-- css/
	|   |   |   |   +-- js/
	|   |   |   |   +-- index.html
	|   |   |   |   +-- doc.html
```
#### Logic
The js/ folder contains the entire logic of this part of application

```
	.
	+-- assets
	|   +-- plugins
	|   |   +-- poll_creation
	|   |   |   +-- pub
	|   |   |   +-- src
	|   |   |   |   +-- css/
	|   |   |   |   +-- js/
	|   |   |   |   |   +-- PDFcreation.js
	|   |   |   |   |   +-- backendcaller.js
	|   |   |   |   |   +-- custommenu.js
	|   |   |   |   |   +-- events.js
	|   |   |   |   |   +-- helper.js
	|   |   |   |   |   +-- index.js
	|   |   |   |   |   +-- navigation.js
	|   |   |   |   |   +-- progressbarTimer.js
```


### Source Cloze Office (Deprecated)
The Poll-Creation Plugin is designed to be accessed from the web-application it self.
BUT it is/should be possible to include the Plugin as an Add-In for Microsoft PowerPoint. This is only tested in version 1.0
The plugin allows to create/edit polls as well as show the result of a poll.

#### Settings

```
  .
  +-- source-cloze-office
  |   +-- manifest.xml
  |   +-- package.json
  |   +-- webpack.config.js
  |   +-- certs
  |   |   +-- server.crt
  |   |   +-- server.key
  |   +-- node_modules
  |   |   +-- ...
```

- [Office Add-ins XML manifest](https://docs.microsoft.com/en-us/office/dev/add-ins/develop/add-in-manifests?tabs=tabid-1) in manifest.xml
- Settings and scripts for starting development server in package.json
- Bundling resources with [Webpack](https://webpack.js.org) and [Babel](https://babeljs.io) in webpack.config.js
- Certificates for development servers (Files empty for security reasons)
- [Node modules](https://nodejs.org/en/) (not included here)

#### Content

```
	.
	+-- source-cloze-office
	|   +-- src
	|   |   +-- index.html
	|   |   +-- index.js
	|   |   +-- app.css
	|   +-- pub
	|   |   +-- prism
	|   |   |   +-- prism.js
	|   |   |   +-- prism.css
	|   |   +-- jQuery
	|   |   |   +-- jQuery.js
	|   |   +-- handlebars
	|   |   |   +-- handlebars.js
	|   |   +-- qrCode
	|   |   |   +-- qrcode.js
	|   |   +-- assets
	|   |   |   +-- source-cloze-logo.png
```

- Main ressources in src
    - Main page in index.html
    - Main script in index.js
    - Stylesheet for add-in in app.css
- Content in prism for code highlighting
- Content in jQuery for  HTML document traversal and manipulation
- Content in handlebars for templates usage
- Content in qrCode for generating QR codes
- Static files in assets
