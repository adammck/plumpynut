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

# returns true or false based on the included
# safe_blasts list to control which blaster
# methods can be invoked from the commandline
def valid_blast(func):
	safe_blasts = ['blast_test']
	if func in safe_blasts:
		return True
	if func not in safe_blasts:
		return False

def blast_test():
	# specific blast for testing
	# (only adam and evan have emails)
	message = "Welcome to uniSMS! Your mobile number is now registered to %(alias)s. Reply with 'help' for more information or get started!"
	peeps = Monitor.objects.filter(email__contains='@')
	return blast(peeps, message, 'alias')

def blast_off():
	# specific blast for kicking of uniSMS
	# in Ethiopia
	message = "Welcome to uniSMS! Your mobile number is now registered to %(alias)s. Reply with 'help' for more information or get started!"
	peeps = Monitor.objects.all()
	return blast(peeps, message, 'alias')


def blast(monitors, message, field=None):
	# mass SMS blaster to send a message to a
	# list of monitors. Messages to uniSMS Monitors
	# can be personalized by including either 
	# %(alias)s or %(first_name)s or %(last_name)s or
	# %(__unicode)s in the message and passing the
	# optional field parameter of either alias or
	# first_name or last_name or __unicode__
	# TODO allow multiple personalized strings
	
	sending = 0 
	sender = kannel.SmsSender("user", "password")
	for m in monitors:
		number = m.phone
		# passing a field implies that
		# the message includes
		# personalizeable strings
		if field:

			# if a field is given, try to
			# substitute the monitor's attribute
			# for the personalized string
			# and send the personalized message
			if hasattr(m, field):
				attribute = getattr(m,field)
				pmessage = message % {field : attribute}
               			sender.send(number, pmessage)
				sending += 1
				print 'Blasted to %d of %d recipients... %s' % (sending, len(monitors), m.details)
			else:
				print "Oops. Monitors don't have %s" % (field)

		# if a field is not given, blast the
		# message directly to all given monitors
		else:
			sender.send(number, message)
			sending += 1
			print 'Blasted to %d of %d monitors...' % (sending, len(monitors))

        print 'Blasted...'
	print '%s' % (message)
	print '...to %d monitors with %d failures' % (sending, (len(monitors) - sending))
	return


def blast_numbers(numbers, message):
	# blasts a message to a list of numbers
	sending = 0
	sender = kannel.SmsSender("user", "password")
	for n in numbers:
		sender.send(n, message)
		sending += 1
		print 'Blasted to %d of %d numbers...' % (sending, len(numbers))
        return 'Blasted %s to %d numbers with %d failures' % (message, sending, (len(numbers) - sending))
		

if __name__ == "__main__":
	import inspect
	import sys

	# if blaster.py is called with arguments
	# try to make sense of them
	if sys.argv:

		# if only one argument is given (in addition to filename)
		# try to call a method with the name of the argument
		if (len(sys.argv) == 2):
			try:

				# check against valid_blast so only
				# legit blasts can be executed
				if (valid_blast(sys.argv[1])):
					func = sys.argv[1] + '()'
					print 'Calling %s ...' % (func)
					eval(func)
				else:
					"Oops. You aren't allowed to call %s from the commandline" % (sys.argv[1])
			except:
				"Oops. I coudn't find a blaster method called %s" % (sys.argv[1])

		numbers = []	
		message = False

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


		# blast away	
		blast_numbers(numbers, message)

	# if blaster.py is called without arguments
	# prompt for arguments
	else:
		numbers = input("Please enter a list of phone numbers to receive SMS blast (eg, ['12345', '12346']): ")
		message = raw_input("Please enter a message to blast to these recipients:").strip()

		blast_numbers(numbers, message)
