from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from inventory.models import *
from webui.utils import * 

def send_sms(request):
	if request.method != 'POST':
        	raise Http404()
	sms_text = request.POST['sms_text'].replace('\r', '')
	recipients = []
    	for m in Monitor.objects.all():
		if request.POST.has_key("monitor-" + str(m.pk)):
			recipients.append(get_object_or_404(Monitor, pk=request.POST["monitor-" + str(m.pk)]))
	
	return HttpResponse(blast(recipients, sms_text), mimetype="text/plain")


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

