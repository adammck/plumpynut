import csv, sys
import httplib, socket, time
from urllib import urlencode
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.core.management import setup_environ

from webui import settings 
setup_environ(settings)
from webui.inventory.models import * 

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
