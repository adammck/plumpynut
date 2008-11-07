#!/usr/bin/env python
# vim: noet

import kannel
from smsapp import *
#from strings import ENGLISH as STR

import csv, sys
from random import choice 
from string import * 
import httplib, socket, time
from urllib import urlencode
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.core.management import setup_environ

from inventory.models import * 

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

        return "Blasted... '%s' ...to %d monitors with %d failures" % (message, sending, (len(monitors) - sending))
	


def import_places():
    filename = file('SNNPR-Table1.csv')
    csvee = filename.read().split('\n')
    reader = csv.DictReader(csvee, quoting = csv.QUOTE_ALL)
    places = []
    for row in reader:
        place = {}
        place['otp']=(row['OTP'])
	place['region']=(row['Region'])
        place['zone']=(row['Zone'])
        place['woreda']=(row['Woreda'])
        places.append(place)
        print place
    for p in places:
	try:
            r = Region.objects.get(name=p['region'])
        except ObjectDoesNotExist:
            r = Region.objects.create(name=p['region'])
        try:
            z = Zone.objects.get(name=p['zone'])
        except ObjectDoesNotExist:
            z = Zone.objects.create(name=p['zone'],region=r)
        try:
            w = Area.objects.get(name=p['woreda'])
        except ObjectDoesNotExist:
            w = Area.objects.create(name=p['woreda'],zone=z)
        try:
            Location.objects.get(name=p['otp'])
        except ObjectDoesNotExist:
            Location.objects.create(name=p['otp'],area=w)
    return places

def export_places():
    places = list(Region.objects.all()) + list(Zone.objects.all()) \
        + list(Area.objects.all()) + list(Location.objects.all())

    out = open("places.json", "w")
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(places, ensure_ascii=False, stream=out)
    return

def export_monitors():
    out = open("peeps.json", "w")
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(Monitor.objects.all(), ensure_ascii=False, stream=out)
    return

def letter():
    from random import choice 
    from string import uppercase 
    return choice(uppercase)

def woreda_code():
    from webui.inventory.models import Area
    code = "W"
    while(len(code) < 4):
        code += letter()
    
    print code
    try:
        Area.objects.get(code=code)
        print '*****'
	return woreda_code()
    except ObjectDoesNotExist:
        return code

def otp_code():
    from webui.inventory.models import Location
    code = ""
    while(len(code) < 4):
        l = letter()
        if(l != "W"):
            code += l

    print code
    try:
        Location.objects.get(code=code)
        print '*****'
        return otp_code() 
    except ObjectDoesNotExist:
        return code
