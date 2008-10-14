#!/usr/bin/env python
# vim: noet

from django.db import models

class Monitor(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	alias = models.CharField(max_length=16, unique=True, help_text="Abbreviated name, lowercase letters")
	phone = models.CharField(max_length=30, blank=True, help_text="e.g., +251912555555")
	email = models.EmailField(blank=True)

	def __unicode__(self):
		ph = self.phone or "unknown"
		return "%s %s [%s]" %\
			(self.first_name, self.last_name, ph)
	
	def _get_full_name(self):
		return "%s %s" % (self.first_name, self.last_name)
	
	full_name = property(_get_full_name)

class Supply(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=4, help_text="Under 4 letters, please")

	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name_plural="Supplies"

	def _get_number_of_reports(self):
		return len(Report.objects.filter(supply=self.id))

	number_of_reports = property(_get_number_of_reports)

class Zone(models.Model):
	name = models.CharField(max_length=100, help_text="Name of zone")

	def __unicode__(self):
		return self.name

	def _get_number_of_areas(self):
		return len(Area.objects.filter(zone=self.id))

	number_of_areas = property(_get_number_of_areas)

class Area(models.Model):
	name = models.CharField(max_length=100, help_text="Name of woreda")
	zone = models.ForeignKey(Zone, help_text="Name of zone")

	def __unicode__(self):
		return self.name
	
	def _get_number_of_locations(self):
		return len(Location.objects.filter(area=self.id))
	
	number_of_locations = property(_get_number_of_locations)

class Location(models.Model):
	name = models.CharField(max_length=100, help_text="Name of OTP")
	code = models.CharField(max_length=4, help_text="Under 4 letters, please")
	area = models.ForeignKey(Area, help_text="Name of woreda")
	
	def __unicode__(self):
		return self.name

class SupplyLocation(models.Model):
	supply = models.ForeignKey(Supply) 
	location = models.ForeignKey(Location, help_text="Name of OTP")
	quantity = models.PositiveIntegerField(blank=True, help_text="Balance at OTP quantity")
	
	def __unicode__(self):
		return "%s at %s" %\
		(self.supply.name, self.location.name)

	class Meta:
		verbose_name_plural="Supplies per Location"

	def _get_area(self):
		return self.location.area

	area = property(_get_area)

class Notification(models.Model):
	monitor = models.ForeignKey(Monitor)
	time = models.DateTimeField(auto_now_add=True)
	notice = models.CharField(blank=True, max_length=160, help_text="Alert from monitor")
	resolved = models.BooleanField(help_text="Has the alert been attended to?")
	
	def __unicode__(self):
		return "%s by %s" %\
		(self.time.strftime("%d/%m/%y"), self.monitor)

class Report(models.Model):
	supply = models.ForeignKey(Supply)
	begin_date = models.DateField()
	end_date = models.DateField()

	def __unicode__(self):
		return "%s report" % self.supply.name
	
	def _get_latest_entry(self):
		try:
			e = Entry.objects.order_by('-time')[0]
		except:
			e = "No Entries"
		return e
	
	def _get_number_of_entries(self):
		return len(Entry.objects.filter(time__gte=self.begin_date).exclude(time__gte=self.end_date))

	number_of_entries = property(_get_number_of_entries)
	latest_entry = property(_get_latest_entry)

class Entry(models.Model):
	monitor = models.ForeignKey(Monitor, help_text="Field monitor")
	supply_location = models.ForeignKey(SupplyLocation, help_text="Reporting location")
	time = models.DateTimeField(auto_now_add=True)
	beneficiaries = models.PositiveIntegerField(blank=True, null=True, help_text="Number of benficiaries")
	quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Quantity")
	consumption = models.PositiveIntegerField(blank=True, null=True, help_text="Consumption quantity")
	balance = models.PositiveIntegerField(blank=True, null=True, help_text="Balance at OTP quantity")

	def __unicode__(self):
		return "%s on %s" %\
		(self.supply_location, self.time.strftime("%d/%m/%y"))
	
	class Meta:
		verbose_name_plural="Entries"

class Message(models.Model):
	transaction = models.PositiveIntegerField(blank=True, null=True)
	monitor = models.ForeignKey(Monitor, blank=True, null=True)
	phone = models.CharField(max_length=30)
	time = models.DateTimeField(auto_now_add=True)
	message = models.CharField(max_length=160)
	is_outgoing = models.BooleanField()
	
	def __unicode__(self):
		if self.is_outgoing: dir = ">>"
		else:                dir = "<<"
		return "%s %s: %s" % (dir, self.monitor, self.message)

