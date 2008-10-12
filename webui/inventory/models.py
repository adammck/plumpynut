#!/usr/bin/env python
# vim: noet

from django.db import models

class Reporter(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	alias = models.CharField(max_length=16, unique=True)
	phone = models.CharField(max_length=30, unique=True)
	email = models.EmailField(blank=True)

	def __unicode__(self):
		ph = self.phone or "unknown"
		return "%s %s [%s]" %\
			(self.first_name, self.last_name, ph)

class Supply(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=4)

	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name_plural="Supplies"

class Location(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=4)

	def __unicode__(self):
		return self.name

class SupplyLocation(models.Model):
	supply = models.ForeignKey(Supply)
	location = models.ForeignKey(Location)
	quantity = models.PositiveIntegerField()
	
	def __unicode__(self):
		return "%s at %s" %\
		(self.supply.name, self.location.name)

	class Meta:
		verbose_name_plural="Supplies per Location"

class Notification(models.Model):
	reporter = models.ForeignKey(Reporter)
	time = models.DateTimeField(auto_now_add=True)
	notice = models.CharField(max_length=160)
	resolved = models.BooleanField()
	
	def __unicode__(self):
		return "%s by %s" %\
		(self.time, self.reporter)

class Report(models.Model):
	supply = models.ForeignKey(Supply)
	begin_date = models.DateField(auto_now_add=True)
	end_date = models.DateField(auto_now=True)

	def __unicode__(self):
		return "%s report" % self.supply.name
	
	def _get_latest_entry(self):
		return Entry.objects.order_by('time')[0]

	latest_entry = property(_get_latest_entry)

class Entry(models.Model):
	report = models.ForeignKey(Report)
	reporter = models.ForeignKey(Reporter)
	supply_location = models.ForeignKey(SupplyLocation)	
	time = models.DateTimeField(auto_now_add=True)
	beneficiaries = models.PositiveIntegerField()
	quantity = models.PositiveIntegerField()
	consumption = models.PositiveIntegerField()
	balance = models.PositiveIntegerField()

	def __unicode__(self):
		return "%s on %s" %\
		(self.supply_location, self.time)
	
	class Meta:
		verbose_name_plural="Entries"
