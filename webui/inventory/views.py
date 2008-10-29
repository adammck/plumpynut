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
