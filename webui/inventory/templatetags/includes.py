#!/usr/bin/env python
# vim: noet

from datetime import datetime

from inventory.models import *
from django import template
register = template.Library()

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
