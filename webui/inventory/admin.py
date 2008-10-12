#!/usr/bin/env python
# vim: noet

from django.contrib import admin
from models import *
from forms import *


class ReporterAdmin(admin.ModelAdmin):
	form = ReporterForm
	list_display = ('full_name', 'alias', 'phone', 'email')

class EntryAdmin(admin.ModelAdmin):
	list_display = ('supply_location', 'time', 'reporter')
	list_filter = ['time']
	date_hierarchy = 'time'
	ordering = ['time']

class LocationAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')

class NotificationAdmin(admin.ModelAdmin):
	list_display = ('reporter', 'time', 'resolved', 'notice')
	list_filter = ['resolved', 'time']
	date_hierarchy = 'time'
	ordering = ['resolved']

class ReportAdmin(admin.ModelAdmin):
	list_display = ('supply', 'begin_date', 'end_date')
	list_filter = ['begin_date']
	radio_fields = {'supply' : admin.HORIZONTAL}

class SupplyAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')

class SupplyLocationAdmin(admin.ModelAdmin):
	list_display = ('location', 'supply', 'quantity')
	radio_fields = {'supply' : admin.HORIZONTAL}


# add our models to the django admin
admin.site.register(Reporter, ReporterAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(SupplyLocation, SupplyLocationAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Entry, EntryAdmin)

