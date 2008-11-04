from django import http
from django.db import models
from django.utils.text import capfirst

def _get_model(app_label, model_name):
	model = models.get_model(app_label, model_name)
	
	# check that the model is valid
	if model is None:
		raise http.Http404(
		"App %r, model %r, not found."\
		% (app_label, model_name))
	
	return model


def to_excel(request, app_label, model_name):
	model = _get_model(app_label, model_name)
	max_depth = 8
	rows = []
	
	
	# this function builds a flat list of column titles (verbose names)
	# recursively, to include as much data as possible in the export
	def build_header(model, depth=0, prefix=""):
		columns = []
		
		for field in model._meta.fields:
			caption = prefix + capfirst(field.verbose_name)
			
			# if this field is a foreign key, then
			# we will recurse to fetch it's fields
			if (hasattr(field, "rel")) and (field.rel is not None) and (depth < max_depth):
				columns.extend(build_header(field.rel.to, depth+1, caption + ": "))
				
			# not a foreign key, so append
			# this column in it's raw form
			else:
				columns.append("<th>%s</th>" % (caption))
		
		return columns
	
	
	# the first row contains no data, just field names
	rows.append("<tr>%s</tr>" % ("".join(build_header(model))))
	
	
	
	# this function is *way* too similar to the function
	# above to warrant its independance. abstraction!
	def build_row(model, instance=None, depth=0):
		columns = []
		
		for field in model._meta.fields:
			if instance:
				cell = getattr(instance, field.name)
			
				# if this field is a foreign key, then
				# we will recurse to fetch it's fields
				if (hasattr(field, "rel")) and (field.rel is not None) and (depth < max_depth):
					columns.extend(build_row(field.rel.to, cell, depth+1))
				
				# not a foreign key, so append
				# this column in it's raw form
				else: columns.append("<td>%s</td>" % (cell))
			
			# the instance that we are iterating is
			# none, but we must fill the column, so
			# insert an empty cell
			else: columns.append("<td></td>")
		return columns
	
	
	# the matrix of dumped data
	for object in model.objects.all():
		row = "".join(build_row(model, object))
		rows.append("<tr>%s</tr>" % (row))
	
	
	# dump it as a simple html table
	html = "<table>%s</table>" % ("\n".join(rows))
	
	# download as an excel spreadsheet
	resp = http.HttpResponse(html, mimetype='application/vnd.ms-excel')
	resp["content-disposition"] = "attachment; filename=%s.xls" % model_name
	return resp

