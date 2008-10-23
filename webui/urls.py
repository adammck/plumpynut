from django.conf.urls.defaults import *
from webui.export import views as ex_views
import os

# everything is done through
# the django admin interface!
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
    (r'^assets/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"}),
    
    # export is magic!
	(r'^(?P<app_label>.+?)/(?P<model_name>.+?)/export/$', ex_views.excel),
     
    # redirect everything else to admin
    (r'^(.*)', admin.site.root),
)

