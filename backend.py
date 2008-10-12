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
	
	# IDENTIFY <ALIAS>
	@kw("identify (letters)", "this is (letters)", "i am (letters)")
	def identify(self, caller, alias):

		# attempt to find the reporter by his/her alias,
		# and notify them that they were recognized
		try:
			reporter = Reporter.objects.get(alias=alias)
			self.send(caller, "Hello, %s" % reporter)
			
		except ObjectDoesNotExist:
			self.send(caller, "Sorry, I don't know anyone called %s" % (alias))
			self.log("Unknown alias: %s" % (alias), "warn")
			return
		
		
		# if this reported is already associated
		# with this number, there's nothing to do
		if reporter.phone == caller:
			return
		
		
		# if anyone else is currently identified
		# by this number, then disassociate them
		try:
			prev = Reporter.objects.get(phone=caller)
			if prev.pk != reporter.pk:
				self.log("%s is no longer %s" % (prev, caller))
				prev.phone = ""
				prev.save()
		
		except ObjectDoesNotExist:
			pass
		
		
		# associate the reporter with this number
		reporter.phone = caller
		reporter.save()
	
	
	# WHO <ALIAS>
	@kw("who is (letters)", "who (letters)", "(letters)\?")
	def who(self, caller, alias):
		
		# attempt to find a reporter by that alias
		# and return their details to the caller
		try:
			reporter = Reporter.objects.get(alias=alias)
			number = reporter.phone or "no number"
			self.send(caller, "%s is %s [%s]" % (alias, reporter, number))
			
		except ObjectDoesNotExist:
			self.send(caller, "Sorry, I don't know anyone called %s" % (alias))


	# WHO AM I
	@kw("who am i", "whoami")
	def whoami(self, caller):
		
		# attempt to find a reporter matching the
		# caller's phone number, and remind them
		try:
			reporter = Reporter.objects.get(phone=caller)
			self.send(caller, "You are %s" % (reporter))
		
		except ObjectDoesNotExist:
			self.send(caller, "Sorry, I don't know who you are")


	# FLAG <NOTICE>
	@kw("flag (.+)")
	def flag(self, caller, notice):
		try:
			r = Reporter.objects.get(phone=caller)
			n = Notification.objects.create(reporter=r, resolved="False", notice=notice)
			self.send(caller, "Notice received")

		except ObjectAssertionError:
			self.send(caller, "Error: Please identify yourself before flagging")


	# nothing matched
	def incoming_sms(self, caller, msg):
		self.send(caller, "ERROR")


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)

