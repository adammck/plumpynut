#!/usr/bin/env python
# vim: noet

import kannel
from smsapp import *
from datetime import date, datetime
from strings import ENGLISH as STR


# import the essentials of django
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from webui import settings
setup_environ(settings)

# import the django models, which should be movd
# somewhere sensible at the earliest opportunity
from webui.inventory.models import *




class App(SmsApplication):
	kw = SmsKeywords()
	
	# non-standard regex chunks
	ALIAS = "([a-z\.]+)"
	
	
	def __get(self, model, **kwargs):
		try:
			# attempt to fetch the object
			return model.objects.get(**kwargs)
		
		# no objects or multiple objects found (in the latter case,
		# something is probably broken, so perhaps we should warn)
		except (ObjectDoesNotExist, MultipleObjectsReturned):
			return None
	
	
	def __identify(self, caller, task=None):
		monitor = self.__get(Monitor, phone=caller)
		
		# if the caller is not identified, then send
		# them a message asking them to do so, and
		# stop further processing
		if not monitor:
			msg = "Please identify yourself"
			if task: msg += " before %s" % (task)
			msg += ", by replying: I AM <USERNAME>"
			raise CallerError(msg)
		
		return monitor
	

	def __monitor(self, alias):
		
		# some people like to include dots
		# in the username (like "a.mckaig"),
		# so we'll merrily ignore those
		clean = alias.replace(".", "")
		
		# attempt to fetch the monitor from db
		# (for now, only by their ALIAS...
		monitor = self.__get(Monitor, alias=clean)
		
		# abort if nothing was found
		if not monitor:
			raise CallerError(
				STR["unknown_alias"] % alias)
		
		return monitor
	
	
	def __guess(self, string, within):
		try:
			from Levenshtein import distance
			import operator
			d = []
		
		# something went wrong (probably
		# missing the Levenshtein library)
		except:
			self.log("Couldn't import Levenshtein library", "err")
			return None
		
		# searches are case insensitive
		string = string.upper()
		
		# calculate the levenshtein distance
		# between each object and the argument
		for obj in within:
			
			# some objects may have a variety of
			# ways of being recognized (code or name)
			if hasattr(obj, "guess"): tries = obj.guess()
			else: tries = [str(obj)]
			
			# calculate the intersection of
			# all objects and their "tries"
			for t in tries:
				dist = distance(str(t).upper(), string)
				d.append((t, obj, dist))
		
		# sort it, and return the closest match
		d.sort(None, operator.itemgetter(2))
		if (len(d) > 0):# and (d[0][1] < 3):
			return d[0]
		
		# nothing was close enough
		else: return None
	
	
	def new_transaction(self, caller):
		id = random.randint(11111111, 99999999)
		
		# when a new transaction is started, create an
		# instance to bind the messages sent and received
		mon = self.__get(Monitor, phone=caller)
		return Transaction.objects.create(
			identity=id,
			phone=caller,
			monitor=mon)
	
	
	
	
	# I AM <ALIAS> ------------------------------------------------------------
	kw.prefix = ["i am", "this is", "identify"]
	
	@kw(ALIAS)
	def identify(self, caller, alias):
		monitor = self.__monitor(alias)
		
		# if this monitor is already associated
		# with this number, there's nothing to do
		if monitor.phone == caller:
			self.respond(STR["ident_again"] % (monitor))

		# if anyone else is currently identified
		# by this number, then disassociate them
		prev = self.__get(Monitor, phone=caller)
		if prev and (prev.pk != monitor.pk):
			prev.phone = ""
			prev.save()

		# associate the monitor with this number
		monitor.phone = caller
		monitor.save()
		
		# the monitor is now identified
		self.respond(STR["ident"] % (monitor))
	
	
	@kw.blank()
	@kw.invalid()
	def identify_fail(self, caller, *msg):
		raise CallerError(STR["ident_help"])




	# WHO AM I ----------------------------------------------------------------
	kw.prefix = ["who am i", "whoami"]

	@kw.blank()
	def whoami(self, caller):

		# attempt to find a monitor matching the
		# caller's phone number, and remind them
		monitor = self.__get(Monitor, phone=caller)
		if monitor: self.respond(STR["whoami"] % (monitor.details))
		else: raise CallerError(STR["whoami_unknown"])
	
	@kw.invalid()
	def whoami_help(self, caller, *msg):
		raise CallerError(STR["whoami_help"])
	
	
	
	
	# WHO IS <ALIAS> ----------------------------------------------------------
	kw.prefix = ["who is", "whois"]
	
	@kw(ALIAS)
	def who(self, caller, alias):
		monitor = self.__monitor(alias)
		self.respond(STR["whois"] % (alias, monitor.details))
	
	@kw.blank()
	@kw.invalid()
	def who_fail(self, caller, *msg):
		raise CallerError(STR["whois_help"])
	
	
	
	
	# ALERT <NOTICE> ----------------------------------------------------------
	kw.prefix = "alert"

	@kw("(whatever)")
	def alert(self, caller, notice):
		monitor = self.__identify(caller, "alerting")
		Notification.objects.create(monitor=monitor, resolved=0, notice=notice)
		self.respond(STR["alert_ok"] % (monitor.alias))
	
	@kw.blank()
	def alert_help(self, caller, *msg):
		raise CallerError(STR["alert_help"])




	# CANCEL ------------------------------------------------------------------
	kw.prefix = "cancel"

	@kw.blank()
	def cancel(self, caller):
		monitor = self.__identify(caller, "cancelling")
		
		try:
			# attempt to find the monitor's
			# most recent entry TODAY
			latest = Entry.objects.filter(
				time__gt=date.today(),
				monitor=monitor)\
				.order_by('-time')[0]
			
			# delete it and notify
			latest.delete()
			self.respond(STR["cancel_ok"] % (monitor.alias))
		
		except (ObjectDoesNotExist, IndexError):
			raise CallerError(STR["cancel_none"] % (monitor.alias))
	
	@kw.invalid()
	def cancel_help(self, caller, *msg):
		raise CallerError(STR["cancel_help"])

	
	
	
	# SUPPLIES ----------------------------------------------------------------
	kw.prefix = ["supplies", "supplys", "supply", "sups"]
	
	@kw.blank()
	def supplies(self, caller):
		self.respond(["%s: %s" % (s.code, s.name)\
			for s in Supply.objects.all()])
	
	@kw.invalid()
	def supplies_help(self, caller):
		raise CallerError(STR["supplies_help"])
	
	
	
	
	# HELP <QUERY> ------------------------------------------------------------
	kw.prefix = ["help", "help me"]
	
	@kw.blank()
	def help_main(self, caller):
		self.respond(STR["help_main"])
	
	@kw("report", "format", "fields")
	def help_report(self, caller):
		self.respond(STR["help_report"])
	
	@kw("register", "identify")
	def help_report(self, caller):
		self.respond(STR["help_reg"])
	
	@kw("alert")
	def help_report(self, caller):
		self.respond(STR["help_alert"])
	
	@kw.invalid()
	def help_help(self, caller):
		self.respond(STR["help_help"])


	
	# CONVERSATIONAL  ------------------------------------------------------------
	kw.prefix = ["ok", "thanks", "thank you"]
	
	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def conv_welc(self, caller):
		monitor = self.__identify(caller, "thanking")
		self.respond(STR["conv_welc"] % (monitor))
	

	kw.prefix = ["hi", "hello", "howdy", "whats up"]

	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def conv_greet(self, caller, whatever=None):
		monitor = self.__get(Monitor, phone=caller)
		if monitor.phone == caller:
			self.respond(STR["ident"] % (monitor))
		self.respond(STR["conv_greet"])


	kw.prefix = ["fuck", "damn", "shit", "bitch"]

	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def conv_swear(self, caller, whatever=None):
		monitor = self.__get(Monitor, phone=caller)
		if monitor.phone == caller:
			self.respond(STR["conv_swear"] % (monitor))
		self.respond(STR["conv_greet"])
	
	

	# <SUPPLY> <PLACE> <BENEFICIERIES> <QUANTITY> <CONSUMPTION> <BALANCE> --
	kw.prefix = ""
	
	@kw("(letters) (letters)(?: (\d+))?(?: (\d+))?(?: (\d+))?(?: (\d+))?")
	def report(self, caller, sup_code, place_code, ben="", qty="", con="", bal=""):
		
		# ensure that the caller is known
		monitor = self.__identify(caller, "reporting")
		
		
		# validate + fetch the supply
		scu = sup_code.upper()
		sup = self.__get(Supply, code=scu)
		if sup is None:
			
			# invalid supply code, so
			# search for a close match
			all_sup = Supply.objects.all()
			sug = self.__guess(scu, all_sup)
			if sug is not None:
				str, obj, dist = sug
			
				# found a close match, so
				# error with a suggestion
				if dist < 5:
					raise CallerError(STR["suggest"]\
					% ("supply code", scu, obj.code, obj.name))
			
			# no close matches (or spellcheck isn't
			# working), so just return error
			raise CallerError(STR["unknown"]\
			% ("supply code", scu))
		
		
		# init variables to avoid
		# pythonic complaints
		loc = None
		area = None
		pcu = place_code.upper()
		
		
		# ...and the "place", which could
		# be either a location or area
		loc = self.__get(Location, code=pcu)
		if loc is None:
			
			# not a valid location, so try area
			area = self.__get(Area, code=pcu)
			if area is None:
				
				# the code was neither a location
				# no area, so search for a close match
				sug = self.__guess(pcu,
					list(Location.objects.all()) +
					list(Area.objects.all()))
				
				if sug is not None:
					str, obj, dist = sug
				
					# found a close match, so
					# error with a suggestion
					if dist < 5:
						raise CallerError(STR["suggest"]\
						% ("OTP or Woreda code", pcu, obj.code, obj.name))
			
				# no close matches (or spellcheck isn't
				# working), so just return error
				raise CallerError(STR["unknown"]\
				% ("OTP or Woreda code", pcu))
		
		
		# fetch the supplylocation object, to update the current stock
		# levels. if it doesn't already exist, just create it, because
		# the administrators probably won't want to add them all...
		
		sp, created = SupplyPlace.objects.get_or_create(supply=sup, location=loc, area=area)
		
		# create the entry object, with
		# no proper validation (todo!)
		Entry.objects.create(
			monitor=monitor,
			supply_place=sp,
			beneficiaries=ben,
			quantity=qty,
			consumption=con,
			balance=bal)
		
		# collate all of the information submitted, to
		# be sent back and checked by the caller
		info = [
			"ben=%s" % (ben or "??"),
			"qty=%s" % (qty or "??"),
			"con=%s" % (con or "??"),
			"bal=%s" % (bal or "??")]
		
		# notify the caller of their new entry
		# this doesn't seem to be localizable
		self.respond(
			"Received %s report for %s %s by %s: %s.\nIf this is not correct, reply with CANCEL" %\
			(sup.name, sp.type, sp.place, monitor, ", ".join(info)))


	


	# NO IDEA WHAT THE CALLER WANTS -------------------------------------------
	
	def incoming_sms(self, caller, msg):
		raise CallerError(STR["error"])




	# LOGGING -----------------------------------------------------------------
	
	# always called by smsapp, to log
	# without interfereing with dispatch
	def before_incoming(self, caller, msg):
		
		# we will log the monitor, if we can identify
		# them by their number. otherwise, log the number
		mon = self.__get(Monitor, phone=caller)
		if mon is None: ph = caller
		else: ph = None
		
		# don't log if the details are the
		# same as the transaction itself
		if mon == self.transaction.monitor: mon = None
		if ph  == self.transaction.phone:   ph  = None
		
		# create a new log entry
		Message.objects.create(
			transaction=self.transaction,
			is_outgoing=False,
			phone=caller,
			monitor=mon,
			message=msg)
	
	
	# as above...
	def before_outgoing(self, recipient, msg):
		
		# we will log the monitor, if we can identify
		# them by their number. otherwise, log the number
		mon = self.__get(Monitor, phone=recipient)
		if mon is None: ph = recipient
		else: ph = None
		
		# don't log if the details are the
		# same as the transaction itself
		if mon == self.transaction.monitor: mon = None
		if ph  == self.transaction.phone:   ph  = None
		
		# create a new log entry
		Message.objects.create(
			transaction=self.transaction,
			is_outgoing=True,
			phone=recipient,
			monitor=mon,
			message=msg)


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)

