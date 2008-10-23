#!/usr/bin/env python
# vim: noet

from django import forms
from models import *
import re

# to match the alias
LOWERCASE_REGEX = re.compile("^[a-z]+$")


class MonitorForm(forms.ModelForm):
	class Meta:
		model = Monitor

	def clean_alias(self):
		data = self.cleaned_data["alias"]
		if not LOWERCASE_REGEX.match(data):
			msg = "This field may only contain lower case letters"
			raise forms.ValidationError(msg)
		
		return data

	
class SupplyForm(forms.ModelForm):
	class Meta:
		model = Supply
	
	def clean_code(self):
		data = self.cleaned_data["code"]
		return data.upper()
