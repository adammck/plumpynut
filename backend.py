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
		rep = self.__get(Reporter, phone=caller)
		
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

		# attempt to find the reporter by his/her alias
		reporter = self.__get(Reporter, alias=alias)
		if not reporter: raise CallerError(
			"I don't know anyone called %s" % (alias))

		# if this reported is already associated
		# with this number, there's nothing to do
		if reporter.phone == caller:
			self.send(caller, "Hello again, %s" % (reporter))
			return

		# if anyone else is currently identified
		# by this number, then disassociate them
		prev = self.__get(Reporter, phone=caller)
		if prev and (prev.pk != reporter.pk):
			prev.phone = ""
			prev.save()

		# associate the reporter with this number
		reporter.phone = caller
		reporter.save()
		
		# the reporter is now identified
		self.send(caller, "Hello, %s" % (reporter))
	
	
	# WHO <ALIAS>
	@kw("who is (letters)", "who (letters)", "(letters)\?")
	def who(self, caller, alias):
		
		# attempt to find a reporter by  alias
		# and return their details to the caller
		reporter = self.__get(Reporter, alias=alias)
		if reporter: msg = "%s is %s" % (alias, reporter)
		else:        msg = "I don't know anyone called %s" % (alias)
		self.send(caller, msg)


	# WHO AM I
	@kw("who am i", "whoami")
	def whoami(self, caller):

		# attempt to find a reporter matching the
		# caller's phone number, and remind them
		reporter = self.__get(Reporter, phone=caller)
		if reporter: msg = "You are %s" % (reporter)
		else:        msg = "I don't know who you are"
		self.send(caller, msg)


	# FLAG <NOTICE>
	@kw("flag", "flag (.+)")
	def flag(self, caller, notice=None):
		reporter = self.__identify(caller, "flagging")
		n = Notification.objects.create(reporter=reporter, resolved="False", notice=notice)
		self.send(caller, "Notice received")

	# HELP!
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
						msg = "<SUPPLY-CODE> <LOCATION> <BENEFICIERIES> <QUANTITY> <CONSUMPTION-QUANTITY> <OTP-BALANCE> <WOREDA-BALANCE>"
						self.send(caller,msg)
		else:
			msg = "UNICEF supply monitoring system help options: help codes, help format <code>, help flags"
			self.send(caller, msg)


	# <SUPPLY-CODE> <LOCATION> <BENEFICIERIES> <QUANTITY> <CONSUMPTION-QUANTITY> <OTP-BALANCE> <WOREDA-BALANCE>
	# pn gdo 7 20
	@kw("(letters) (letters) (numbers) (numbers)")
	def report(self, caller, sup_code, loc_code, benef, qty):
		
		# ensure that the caller is known
		reporter = self.__identify(caller, "reporting")
		
		# validate + fetch the supply
		sup = self.__get(Supply, code=sup_code)
		if not sup: raise CallerError(
			"Invalid supply code: %s" % (sup_code))
		
		# ...and the location
		loc = self.__get(Location, code=loc_code)
		if not loc: raise CallerError(
			"Invalid location code: %s" % (loc_code))
		
		# fetch the supplylocation object, to update the current stock
		# levels. if it doesn't already exist, just create it, because
		# the administrators probably won't want to add every supply
		# to every location...
		sl = SupplyLocation.objects.get_or_create(supply=sup, location=loc)



	# nothing matched
	def incoming_sms(self, caller, msg):
		self.send(caller, "ERROR")


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)

