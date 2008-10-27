#!/usr/bin/env python
# vim: noet

import kannel
from smsapp import *
from strings import ENGLISH as STR


# import the essentials of django
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from webui import settings
setup_environ(settings)

# import the django models, which should be movd
# somewhere sensible at the earliest opportunity
from webui.inventory.models import *

def blastTest():
	message = "Welcome to uniSMS! Your number is now registered to %(alias)s. Reply with 'help' for more information."
        numbers = ['251911505181', '251911385921']
	return blast(numbers, message, 'alias')

def blastOff():
	message = "Welcome to uniSMS! Your number is now registered to %(alias)s. Reply with 'help' for more information."
	peeps = Monitor.objects.all()
	numbers = []
	for p in peeps:
		numbers.append(p.phone)
	return blast(numbers, message, 'alias')


def blast(numbers, message, field=None):
	sending = 0 
	sender = kannel.SmsSender("user", "password")
	for n in numbers:
		if field:
			try:
				m = Monitor.objects.get(phone=n)
				if hasattr(m, field):
					attribute = getattr(m,field)
					pmessage = message % {field : attribute}
                			sender.send(n, pmessage)
					sending += 1
					print 'Blasted to %d of %d recipients...' % (sending, len(numbers))
					pass
				else:
					print "Oops. Monitors don't have %s" % (field)
					pass
			except ObjectDoesNotExist:
				print "Oops. I coudn't find a monitor for %s" % (n)
				pass
		else:
			sender.send(n, message)
			sending += 1
			print 'Blasted to %d of %d recipients...' % (sending, len(numbers))
        return 'Blasted %s to %d numbers with %d failures' % (message, sending, (len(numbers) - sending))

if __name__ == "__main__":
	import sys
	# if blaster.py is called with arguments
	# try to make sense of them
	if sys.argv:
		numbers = []	
		message = False
		field = None
		# iterate all given arguments
		# except for the first (./blaster.py)
		for arg in sys.argv[1:]:
			# strip brackets and commas from the argument
			# (we expect a list of numbers as strings)
			num = arg.strip('[,]')
			if num.isdigit():
				numbers.append(num)
			# if there are no more numbers and message
			# has not been set, assume this arg is
			# the message
			else:
				if not message:
					message = arg
			# if we are still looping and have a
			# message, try to assign optional
			# field argument
			try:
				if(message):
					field = arg
			except:
				field = None
		# blast away	
		blast(numbers, message, field)

	# if blaster.py is called without arguments
	# prompt for arguments
	else:
		numbers = input("Please enter a list of phone numbers to receive SMS (eg, ['12345', '12346']) : ")
		message = raw_input("Please enter a message to blast to these recipients (you may specify a personalized word by using %(alias)s or %(first_name)s or %(last_name)s or %(__unicode__)s ):").strip()
		field = raw_input("Please enter any personalized word from your message or press enter to send (eg, alias or first_name or last_name or __unicode__):").strip()

		blast(numbers, message, field)
