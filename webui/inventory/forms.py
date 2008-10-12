#!/usr/bin/env python
# vim: noet

from django import forms
from models import *
import re

# to match the alias
LETTERS_REGEX = re.compile("^[a-z]+$")


class ReporterForm(forms.ModelForm):
	class Meta:
		model = Reporter

	def clean_alias(self):
		data = self.cleaned_data["alias"]
		if not LETTERS_REGEX.match(data):
			msg = "This field may only contain lower case letters"
			raise forms.ValidationError(msg)
		
		return data

