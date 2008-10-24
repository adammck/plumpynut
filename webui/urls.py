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
    
    # exporting is magic!
	(r'^(?P<app_label>.+?)/(?P<model_name>.+?)/export/excel/$', ex_views.to_excel),
	(r'^(?P<app_label>.+?)/(?P<model_name>.+?)/export/print/$', in_views.to_print),
     
    # redirect everything else to admin
    (r'^(.*)', admin.site.root),
)

