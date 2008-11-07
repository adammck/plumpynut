from django.conf.urls.defaults import *
from webui.export import views as ex_views
from webui.inventory import views as in_views
import os

# everything is done through
# the django admin interface!
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
    (r'^assets/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"}),
    
	(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to',
		{'url': '/assets/favicon.ico'}),
    
    # exporting is magic!
	(r'^(?P<app_label>.+?)/(?P<model_name>.+?)/export/excel/$', ex_views.to_excel),
	(r'^(?P<app_label>.+?)/(?P<model_name>.+?)/export/print/$', in_views.to_print),
	(r'^export/$', ex_views.export),
     
    # send sms
	(r'^send_sms/$', 'inventory.views.send_sms'),
	
	# various google maps
	(r'^map/entries/$', in_views.map_entries),

    # redirect everything else to admin
    (r'^(.*)', admin.site.root),
)

