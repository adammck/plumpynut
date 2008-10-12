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
	
	def __get_reporter(self, **kwargs):
		try:
			r = Reporter.objects.get(**kwargs)
			return r
		
		except ObjectDoesNotExist:
			return None
	
	
	# IDENTIFY <ALIAS>
	@kw("identify (letters)", "this is (letters)", "i am (letters)")
	def identify(self, caller, alias):

		# attempt to find the reporter by his/her alias,
		# and notify them that they were recognized
		reporter = self.__get_reporter(alias=alias)
		if not reporter:
			self.send(caller, "Sorry, I don't know anyone called %s" % (alias))
			self.log("Unknown alias: %s" % (alias), "warn")
			return

		# if this reported is already associated
		# with this number, there's nothing to do
		if reporter.phone == caller:
			self.send(caller, "Hello again, %s" % (reporter))
			return

		# if anyone else is currently identified
		# by this number, then disassociate them
		prev = self.__get_reporter(phone=caller)
		if prev and (prev.pk != reporter.pk):
			prev.phone = ""
			prev.save()

		# associate the reporter with this number
		self.send(caller, "Hello, %s" % (reporter))
		reporter.phone = caller
		reporter.save()
	
	
	# WHO <ALIAS>
	@kw("who is (letters)", "who (letters)", "(letters)\?")
	def who(self, caller, alias):
		
		# attempt to find a reporter by  alias
		# and return their details to the caller
		reporter = self.__get_reporter(alias=alias)
		if reporter: msg = "%s is %s" % (alias, reporter)
		else:        msg = "I don't know anyone called %s" % (alias)
		self.send(caller, msg)


	# WHO AM I
	@kw("who am i", "whoami")
	def whoami(self, caller):

		# attempt to find a reporter matching the
		# caller's phone number, and remind them
		reporter = self.__get_reporter(phone=caller)
		if reporter: msg = "You are %s" % (reporter)
		else:        msg = "I don't know who you are"
		self.send(caller, msg)


	# FLAG <NOTICE>
	@kw("flag (.+)")
	def flag(self, caller, notice):
		reporter = self.__get_reporter(phone=caller)
		n = Notification.objects.create(reporter=reporter,\
		resolved="False", notice=notice)
		self.send(caller, "Notice received")


	# nothing matched
	def incoming_sms(self, caller, msg):
		self.send(caller, "ERROR")


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)

