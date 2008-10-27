#!/usr/bin/env python
# vim: noet

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from webui.utils import otp_code, woreda_code 

class Monitor(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	alias = models.CharField(max_length=16, unique=True, help_text="Abbreviated name, lowercase letters")
	phone = models.CharField(max_length=30, blank=True, help_text="e.g., +251912555555")
	email = models.EmailField(blank=True)
	
	class Meta:
		verbose_name = "Field Monitor"
	
	# the string version of monitors
	# now contains only their name
	def __unicode__(self):
		return "%s %s" %\
			(self.first_name,
			self.last_name)
	
	# 'summarize' the field monitor by
	# returning his full name and number
	def _get_details(self):
		ph = self.phone or "unknown"
		return "%s (%s)" % (self, ph)
	details = property(_get_details)

class Supply(models.Model):
	name = models.CharField(max_length=100, unique=True)
	code = models.CharField(max_length=20, unique=True)
	
	class Meta:
		verbose_name_plural="Supplies"

	def __unicode__(self):
		return self.name

	
	def guess(self):
		return [self.name, self.code]
	
	def _get_number_of_reports(self):
		return len(Report.objects.filter(supply=self.id))

	number_of_reports = property(_get_number_of_reports)

class Region(models.Model):
	name = models.CharField(max_length=100, unique=True, help_text="Name of region")

	def __unicode__(self):
		return self.name

	def _get_number_of_zones(self):
		return len(Zone.objects.filter(region=self.id))

	number_of_zones = property(_get_number_of_zones)

class Zone(models.Model):
	name = models.CharField(max_length=100, unique=True, help_text="Name of zone")
	region = models.ForeignKey(Region, help_text="Name of region")
	
	class Meta:
		ordering = ('region', 'name')
	
	def __unicode__(self):
		return self.name

	def _get_number_of_areas(self):
		return len(Area.objects.filter(zone=self.id))

	number_of_woredas = property(_get_number_of_areas)

class Area(models.Model):
	name = models.CharField(max_length=100, unique=True, help_text="Full name of woreda")
	code = models.CharField(max_length=20, unique=True, editable=False)
	zone = models.ForeignKey(Zone, help_text="Name of zone")
	
	def save(self):
		# if this area does not already
		# have a code, assign a new one
		if(self.code == ""):
			c = woreda_code()
			self.code = c
		
		# invoke parent to save data
		models.Model.save(self)
	
	class Meta:
		verbose_name = "Woreda"
	
	def __unicode__(self):
		return self.name
	
	def _get_number_of_locations(self):
		return len(Location.objects.filter(area=self.id))
	
	number_of_OTPs = property(_get_number_of_locations)

class Location(models.Model):
	name = models.CharField(max_length=100, help_text="Full name of the OTP")
	code = models.CharField(max_length=20, unique=True, editable=False)
	area = models.ForeignKey(Area, help_text="Name of woreda")
	
	def save(self):
		# if this OTP does not already
		# have a code, assign a new one
		if(self.code == ""):
			c = otp_code()
			self.code = c
		
		# invoke parent to save data
		models.Model.save(self)
	
	class Meta:
		verbose_name = "OTP"
	
	def __unicode__(self):
		return self.name

	def _get_woreda(self):
    		return self.area

	woreda = property(_get_woreda)

class SupplyPlace(models.Model):
	supply = models.ForeignKey(Supply) 
	location = models.ForeignKey(Location, blank=True, null=True, help_text="Name of OTP")
	area = models.ForeignKey(Area, blank=True, null=True, help_text="Name of Woreda")
	quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Balance at OTP")
	
	def __unicode__(self):
		return "%s at %s (%s)" %\
		(self.supply.name, self.place, self.type)

	class Meta:
		verbose_name_plural="Supplies per OTP or Woreda"
	
	def _get_place(self):
		if self.location: return self.location
		elif self.area:   return self.area
		else:             return "Unknown"
	place = property(_get_place)
	
	def _get_type(self):
		if self.location: return "OTP"
		elif self.area:   return "Woreda"
		else:             return "Unknown"
	type = property(_get_type)
		
	def _get_area(self):
		if self.location: return self.location.area
		elif self.area:   return self.area
		else:             return "Unknown"
	woreda = property(_get_area)

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
	supply_place = models.ForeignKey(SupplyPlace)

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
	supply_place = models.ForeignKey(SupplyPlace, help_text="Reporting location")
	time = models.DateTimeField(auto_now_add=True)
	beneficiaries = models.PositiveIntegerField(null=True, help_text="Number of benficiaries")
	quantity = models.PositiveIntegerField(null=True, help_text="Quantity")
	consumption = models.PositiveIntegerField(null=True, help_text="Consumption quantity")
	balance = models.PositiveIntegerField(null=True, help_text="Balance at OTP")

	def __unicode__(self):
		return "%s on %s" %\
		(self.supply_place, self.time.strftime("%d/%m/%y"))
	
	class Meta:
		verbose_name_plural="Entries"


class Transaction(models.Model):
	identity = models.PositiveIntegerField(blank=True, null=True)
	
	# the monitor (or number, if monitor isn't known)
	# who triggered the creation of this transaction
	# ----
	# todo: validate that at least one of these is provided
	phone = models.CharField(max_length=30, blank=True, null=True)
	monitor = models.ForeignKey(Monitor, blank=True, null=True)
	
	def __unicode__(self):
		return unicode(self.identity)


class Message(models.Model):
	transaction = models.ForeignKey(Transaction, blank=True, null=True)
	
	# these are only needed if the message is not bound to a
	# transaction, or the message going out to someone else
	phone = models.CharField(max_length=30, blank=True, null=True)
	monitor = models.ForeignKey(Monitor, blank=True, null=True)
	
	# but every message has these
	time = models.DateTimeField(auto_now_add=True)
	message = models.CharField(max_length=160)
	is_outgoing = models.BooleanField()
	
	# todo: what is this for? the screen log?
	def __unicode__(self):
		if self.is_outgoing: dir = ">>"
		else:                dir = "<<"
		return "%s %s: %s" % (dir, self.monitor, self.message)

