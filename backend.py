#!/usr/bin/env python
# vim: noet

from smsapp import *
import kannel


# import the essentials of django
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from webui import settings
setup_environ(settings)

# import the django models
from webui.inventory.models import *




class App(SmsApplication):
	kw = SmsKeywords()
	
	def __get(self, model, **kwargs):
		try: return model.objects.get(**kwargs)
		except ObjectDoesNotExist: return None
	
	def __identify(self, caller, task=None):
		rep = self.__get(Monitor, phone=caller)
		
		# if the caller is not identified, then send
		# them a message asking them to do so, and
		# stop further processing
		if not rep:
			msg = "Please identify yourself"
			if task: msg += " before %s" % (task)
			raise CallerError(msg)
		
		return rep
	
	
	# IDENTIFY <ALIAS>
	@kw("identify (letters)", "this is (letters)", "i am (letters)")
	def identify(self, caller, alias):

		# attempt to find the monitor by his/her alias
		monitor = self.__get(Monitor, alias=alias)
		if not monitor: raise CallerError(
			"I don't know anyone called %s" % (alias))

		# if this reported is already associated
		# with this number, there's nothing to do
		if monitor.phone == caller:
			self.send(caller, "Hello again, %s" % (monitor))
			return

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
		self.send(caller, "Hello, %s" % (monitor))
	
	
	# WHO <ALIAS>
	@kw("who is (letters)", "who (letters)", "(letters)\?")
	def who(self, caller, alias):
		
		# attempt to find a monitor by  alias
		# and return their details to the caller
		monitor = self.__get(Monitor, alias=alias)
		if monitor: msg = "%s is %s" % (alias, reporter)
		else:        msg = "I don't know anyone called %s" % (alias)
		self.send(caller, msg)


	# WHO AM I
	@kw("who am i", "whoami")
	def whoami(self, caller):

		# attempt to find a monitor matching the
		# caller's phone number, and remind them
		monitor = self.__get(Monitor, phone=caller)
		if monitor: msg = "You are %s" % (reporter)
		else:        msg = "I don't know who you are"
		self.send(caller, msg)


	# FLAG <NOTICE>
	@kw("flag", "flag (.+)")
	def flag(self, caller, notice=None):
		monitor = self.__identify(caller, "flagging")
		Notification.objects.create(monitor=reporter, resolved="False", notice=notice)
		self.send(caller, "Notice received")

	
	# SUPPLIES
	@kw("supplies", "supplys", "sups")
	def supplies(self, caller):
		all_sup = Supply.objects.all()
		flat_sup = ["%s: %s" % (s.code, s.name) for s in all_sup]
		self.send(caller, "\n".join(flat_sup))
	
	
	# LOCATIONS
	@kw("locations", "locs")
	def locations(self, caller):
		all_loc = Location.objects.all()
		flat_loc = ["%s: %s" % (l.code, l.name) for l in all_loc]
		self.send(caller, "\n".join(flat_loc))


	# HELP <QUERY> <CODE>
	@kw("help", "help (letters)", "help (letters) (letters)")
	def help(self, caller, query=None, code=None):
		if(query):
			if(query == "codes"):
				supplies = Supply.objects.all()
				msg = ["%s: %s" % (s.name, s.code) for s in supplies]
				self.send(caller,msg)

			if(query == "flags"):
				msg = "Send 'flag' followed by a notice that will be reviewed by HQ. Please include your location, if applicable."
				self.send(caller,msg)

			if(code):
				if(query == "format"):
					if(code.upper() == "PN"):
						msg = "<SUPPLY-CODE> <LOCATION> <BENEFICIERIES> <QUANTITY> <CONSUMPTION-QUANTITY> <OTP-BALANCE>"
						self.send(caller,msg)
		else:
			msg = "UNICEF supply monitoring system help options: help codes, help format <code>, help flags"
			self.send(caller, msg)


	# <SUPPLY-CODE> <LOCATION> <BENEFICIERIES> <QUANTITY> <CONSUMPTION-QUANTITY> <OTP-BALANCE> 
	# pn gdo 7 20
	@kw("([a-z]{1,4}) ([a-z]{1,4})(?: (\d+))?(?: (\d+))?(?: (\d+))?(?: (\d+))?")
	def report(self, caller, sup_code, loc_code, ben=None, qty=None, con=None, bal=None):
		
		# ensure that the caller is known
		rep = self.__identify(caller, "reporting")
		
		# validate + fetch the supply
		sup = self.__get(Supply, code=sup_code.upper())
		if not sup: raise CallerError(
			"Invalid supply code: %s" % (sup_code))
		
		# ...and the location
		loc = self.__get(Location, code=loc_code.upper())
		if not loc: raise CallerError(
			"Invalid location code: %s" % (loc_code))
		
		# fetch the supplylocation object, to update the current stock
		# levels. if it doesn't already exist, just create it, because
		# the administrators probably won't want to add them all...
		sl, created = SupplyLocation.objects.get_or_create(supply=sup, location=loc)
		
		# create the entry object, with
		# no proper validation (todo!)
		Entry.objects.create(
			monitor=rep,
			supply_location=sl,
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
		self.send(caller,
			"Received %s report for %s by %s.\n%s\nIf this is not correct, reply with CANCEL" %\
			(sup.name, loc.name, rep, ", ".join(info)))



	# nothing matched
	def incoming_sms(self, caller, msg):
		self.send(caller, "Oops. I didn't recognize '%s'. Please reply 'help' for more information."%\
			msg)


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)

