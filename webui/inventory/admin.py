#!/usr/bin/env python
# vim: noet

from django.contrib import admin
from models import *
from forms import *


class ReporterAdmin(admin.ModelAdmin):
	form = ReporterForm


# add our models to the django admin
admin.site.register(Reporter, ReporterAdmin)
admin.site.register(Supply)
admin.site.register(Location)
admin.site.register(SupplyLocation)
admin.site.register(Notification)

