#!/usr/bin/env python
# vim: noet

from datetime import datetime, timedelta
import fpformat
import os
import sys
import math

from pygooglechart import SimpleLineChart, Axis, PieChart2D, StackedVerticalBarChart

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404

from django.core.management import setup_environ
from webui import settings
setup_environ(settings)

from webui.inventory.models import *
from webui.utils import * 

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '..'))


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

def refresh_graphs():
	print graph_entries()
	print graph_otps()
	print graph_monitors()
	print graph_avg_stat()

	return 'refreshed graphs'

def graph_entries(num_days=14):
	# its a beautiful day
	today = datetime.today().date()

	# step for x axis
	step = timedelta(days=1)

	# empties to fill up with data
	counts = []
	dates = []

	# only get last two weeks of entries 
	day_range = timedelta(days=num_days)
	entries = Entry.objects.filter(
			time__gt=(today	- day_range))
	
	# count entries per day
	for day in range(num_days):
		count = 0
		d = today - (step * day)
		for e in entries:
			if e.time.day == d.day:
				count += 1
		dates.append(d.day)
		counts.append(count)
    
    	line = SimpleLineChart(400, 100, y_range=(0, 100))
	line.add_data(counts)
	line.set_axis_labels(Axis.BOTTOM, dates)
	line.set_axis_labels(Axis.LEFT, ['', 50, 100])
	line.set_colours(['0091C7'])
	line.download('webui/graphs/entries.png')
	
	return 'saved entries.png' 


def graph_monitors(num_days=14):
	# pie chart of monitors
	day_range = timedelta(days=num_days)
	reported = 0
	mons = Monitor.objects.all()
	for m in mons:
		if m.latest_report != 'N/A':
			if m.latest_report.time.date() > (datetime.today().date() - day_range):
				reported += 1

	chart = PieChart2D(300, 100)
	chart.add_data([(len(mons)-reported), reported])
	#chart.set_pie_labels(['', 'Reporting Monitors'])
	chart.set_legend(['Non-reporting Monitors', 'Reporting Monitors'])
	chart.set_colours(['0091C7','0FBBD0'])
	chart.download('webui/graphs/monitors.png')

	return 'saved monitors.png' 
	

def graph_otps():
	# pie chart of otps
	ent = Entry.objects.all()
	visited = 0
	for e in ent:
		if e.supply_place.type == 'OTP':
			visited += 1

	otps = len(Location.objects.all())
	percent_visited = float(visited)/float(otps)
	percent_not_visited = float(otps - visited)/float(otps)

	chart = PieChart2D(300, 100)
	chart.add_data([(percent_not_visited*100), (percent_visited*100)])
	#chart.set_pie_labels(['', 'Visited OTPs'])
	chart.set_legend(['Non-visited OTPs', 'Visited OTPs'])
	chart.set_colours(['0091C7','0FBBD0'])
	chart.download('webui/graphs/otps.png')

	return 'saved otps.png' 
	

def graph_avg_stat():	
	# bar chart of avg wor and otp stats	
	# and pie chart of avg otp coverage

	# lots of variables
	# for summing all these data
	# o_num => number of otps
	# w_q => woreda quantity
	# etc
	o_num = 0
	o_b = 0
	o_q = 0
	o_c = 0
	o_s = 0

	w_num = 0
	w_b = 0
	w_q = 0
	w_c = 0
	w_s = 0

	# in first pass we're gathering
	# a list of woredas that have been
	# visited, along with summing all
	# their data
	woreda_list = []

	ent = Entry.objects.all()

	for e in ent:
		if e.supply_place.type == 'Woreda':
			w_num += 1
			if e.beneficiaries is not None:
				w_b += e.beneficiaries
			if e.quantity is not None:
				w_q += e.quantity
			if e.consumption is not None:
				w_c += e.consumption
			if e.balance is not None:
				w_s += e.balance
			woreda_list.append(e.supply_place.area)

	# this is obnoxious but the best
	# way python will allow making a
	# dict from a list
	woredas = { " " : 0}
	woredas = woredas.fromkeys(woreda_list, 0)

	# second pass to gather otp sums
	# why a second pass? bc we need to
	# add visted otp sums to the woreda dict 
	for e in ent:
		if e.supply_place.type == 'OTP':
			o_num += 1
			if e.beneficiaries is not None:
				o_b += e.beneficiaries
			if e.quantity is not None:
				o_q += e.quantity
			if e.consumption is not None:
				o_c += e.consumption
			if e.balance is not None:
				o_s += e.balance

			if e.supply_place.location.area in woredas:
				woredas[e.supply_place.location.area] += 1
	
	# make a list of tuples from dict
	# (woreda obj, num-of-its-otps-that-have-been-visited)
	woreda_list = woredas.items()

	# a for average otps visited
	a = 0

	# n for number of total otps in woreda
	n = 0

	# count total otps and compute average
	# and add this to the global sums
	for t in woreda_list:
		n += t[0].number_of_OTPs
		if t[1] != 0:
			a += float(t[0].number_of_OTPs)/float(t[1])
	
	# normalize for graphing
	d_a = float(a)/float(n)
	d_n = 1 - d_a

	# average otp and woreda data, 
	o_b = (float(o_b)/float(o_num))
	o_q = (float(o_q)/float(o_num))
	o_c = (float(o_c)/float(o_num))
	o_s = (float(o_s)/float(o_num))
	w_b = (float(w_b)/float(w_num))
	w_q = (float(w_q)/float(w_num))
	w_c = (float(w_c)/float(w_num))
	w_s = (float(w_s)/float(w_num))

	pie = PieChart2D(300, 100)
	pie.add_data([(d_n*100), (d_a*100)])
	#pie.set_pie_labels(['', 'Avg visited OTPs per woreda'])
	pie.set_legend(['Avg non-visted OTPs per woreda', 'Avg visited OTPs per woreda'])
	pie.set_colours(['0091C7','0FBBD0'])
	pie.download('webui/graphs/avg_otps.png')

	#bar = StackedVerticalBarChart(400,100)
	#bar.set_colours(['4d89f9','c6d9fd'])
	#bar.add_data([o_b, o_q, o_c, o_s])
	#bar.add_data([w_b, w_q, w_c, w_s])
	#bar.set_axis_labels(Axis.BOTTOM, ['Ben', 'Qty', 'Con', 'Bal'])
	#bar.download('webui/graphs/avg_stat.png')

	return 'saved avg_stat.png' 

def map_entries():
	pass

