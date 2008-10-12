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
	
	# IDENTIFY <NAME>
	@kw("identify (slug)")
	def identify(self, caller, alias):
		try:
			r = Reporter.objects.get(alias=alias)
			self.send(caller, "Hello, %s" % r)
			
		except ObjectDoesNotExist:
			self.send(caller, "Error: There is no such reporter as '%s'" % (alias))

	# nothing matched	
	def incoming_sms(self, caller, msg):
		self.send(caller, "ERROR")


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()

# wait for interrupt
while True: time.sleep(1)

