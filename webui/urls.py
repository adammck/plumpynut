from django.conf.urls.defaults import *
import os

# everything is done through
# the django admin interface!
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
    (r'^assets/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"}),
    
    # redirect everything else to admin
    (r'^(.*)', admin.site.root),
)

