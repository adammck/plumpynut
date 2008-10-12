#!/usr/bin/env python
from smsapp import *
import kannel

class PlumpynutApp(SmsApplication):
	def incoming_sms(self, caller, msg):
		self.send(caller, "wat")

app = PlumpynutApp(backend=kannel, sender_args=["user", "pass"])
app.run()

# wait for interrupt
while True: time.sleep(1)

