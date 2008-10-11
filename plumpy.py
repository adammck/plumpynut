#!/usr/bin/env python
from smsapp import *
import kannel

class PlumpynutApp(SmsApplication):
	def incoming_sms(self, caller, msg):
		self.send(caller, "Wat")

app = PlumpynutApp(backend=kannel, sender_args=["user", "pass"])
app.run()

while True:
	time.sleep(1)
