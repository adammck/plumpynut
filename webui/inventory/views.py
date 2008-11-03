from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from inventory.models import *
from webui.utils import * 

def send_sms(request):
	
	# there is no view, only post requests
	# from the form on the dashboard
	if request.method != 'POST':
		raise Http404()

	# remove line feeds (todo: the sending backend
	# should deal with this automatically)
	sms_text = request.POST['message'].replace('\r', '')

	# iterate all monitors, and if they're in the
	# POST form (ie, their checkbox was ticked),
	# add them to the recipients array
	recipients = []
	for m in Monitor.objects.all():
		if request.POST.has_key("monitor-" + str(m.pk)):
			recipients.append(m)

	# perform the "blast" and dump the output
	# (short summary of what was sent, and what
	# failed) in a very bland and temporary page
	result = blast(recipients, sms_text)
	return HttpResponse(result, mimetype="text/plain")


def to_print(request, app_label, model_name):
	data = []
	
	# only OTPs are supported right now
	if app_label != "inventory"\
	or model_name != "location":
		raise http.Http404(
		"App %r, model %r, not supported."\
		% (app_label, model_name))
	
	# collate regions as top-level sections
	for region in Region.objects.all().order_by('name'):
		zones = region.zone_set.all().order_by('name')
		for zone in zones:
			
			# collate OTPs by woreda, and perform
			# magic to make a four-column table 
			# using django's crappy templates
			areas = zone.area_set.all().order_by('name')
			for area in areas:
				locations = area.location_set.all().order_by('name')
		
				n = 0
				for location in locations:
					setattr(location, "left", (n+1) % 2)
					setattr(location, "right", n % 2)
					n += 1
		
				# list all OTPs per woreda
				setattr(area, "locations", locations)
			setattr(zone, "areas", areas)
		setattr(region, "zones", zones)
		data.append(region)
	
	return render_to_response("reference.html", {"regions": data})


def map_entries(request):
	return render_to_response("map/entries.html")

