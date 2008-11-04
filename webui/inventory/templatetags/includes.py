#!/usr/bin/env python
# vim: noet

from datetime import datetime, timedelta
import fpformat

from inventory.models import *
from django import template
register = template.Library()

@register.inclusion_tag("graph.html")
def incl_graph():
	# line graph of entries
	# its a beautiful day
	today = datetime.today().date()

	# step for x axis
	step = timedelta(days=1)

	# empties to fill up with data
	counts = []
	dates = []

	# only get last two weeks of entries 
	day_range = timedelta(days=14)
	entries = Entry.objects.filter(
			time__gt=(today	- day_range))
	
	# count entries per day
	for day in range(14):
		count = 0
		d = today - (step * day)
		for e in entries:
			if e.time.day == d.day:
				count += 1
		dates.append(d.day)
		counts.append(count)

	# pie chart of monitors
	reported = 0
	mons = Monitor.objects.all()
	for m in mons:
		if m.latest_report != 'N/A':
			if m.latest_report.time.date() > (datetime.today().date() - day_range):
				reported += 1
	
	# pie chart of otps
	ent = Entry.objects.all()
	visited = 0
	for e in ent:
		if e.supply_place.type == 'OTP':
			visited += 1

	otps = len(Location.objects.all())
	percent_visited = float(visited)/float(otps)
	percent_not_visited = float(otps - visited)/float(otps)
	

	# bar chart of avg wor and otp stats	
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

	o_b = fpformat.fix(float(o_b)/float(o_num), 1)
	o_q = fpformat.fix(float(o_q)/float(o_num), 1)
	o_c = fpformat.fix(float(o_c)/float(o_num), 1)
	o_s = fpformat.fix(float(o_s)/float(o_num), 1)
	w_b = fpformat.fix(float(w_b)/float(w_num), 1)
	w_q = fpformat.fix(float(w_q)/float(w_num), 1)
	w_c = fpformat.fix(float(w_c)/float(w_num), 1)
	w_s = fpformat.fix(float(w_s)/float(w_num), 1)

	return { "counts" : counts, "dates" : dates,\
		"unreported": (len(mons)-reported), \
		"reported" : reported, "visited" : fpformat.fix(percent_visited*100, 1),\
		"not_visited" : fpformat.fix(percent_not_visited*100, 1),\
		"o_b" : o_b, "o_q" : o_q, "o_c" : o_c, "o_s" : o_s,\
		"w_b" : w_b, "w_q" : w_q, "w_c" : w_c, "w_s" : w_s} 

@register.inclusion_tag("grid.html")
def incl_grid():
	today = datetime.today().date()
	return {"entries": Entry.objects.filter(time__gte=today)}

@register.inclusion_tag("messages.html")
def incl_messages(type):
	
	if type == "in":
		capt = "Incomming"
		og = False
		
	elif type == "out":
		capt = "Outgoing"
		og = True
	
	return {
		"caption": "Recent %s Messages" % (capt),
		"messages": Message.objects.filter(is_outgoing=og).order_by("-time")[:10]
	}


@register.inclusion_tag("send.html")
def incl_send():
	return {
		"monitors": Monitor.objects.all()
	}

@register.inclusion_tag("transactions.html")
def incl_transactions():
	return {
		"transactions": Transaction.objects.filter().order_by("-id")[:10]
	}


@register.inclusion_tag("notifications.html")
def incl_notifications():
	return {
		"caption": "Unresolved Notifications",
		"notifications": Notification.objects.filter(resolved=False).order_by("-time")
	}
