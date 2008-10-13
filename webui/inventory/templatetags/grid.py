#!/usr/bin/env python
# vim: noet

from inventory.models import *
from django import template
register = template.Library()

@register.inclusion_tag("grid.html")
def incl_grid():
	return {"entries": Entry.objects.all()}

