from django import http
from django.db import models
from django.utils.text import capfirst


def excel(request, app_label, model_name):
	model = models.get_model(app_label, model_name)
	rows = []
	
	# check that the model is valid
	if model is None:
		raise http.Http404(
		"App %r, model %r, not found."\
		% (app_label, model_name))
	
	# the first row of column names
	columns = ["<th>%s</th>" % capfirst(field.verbose_name) for field in model._meta.fields]
	rows.append("<tr>%s</tr>" % "".join(columns))
	
	# the matrix of dumped data
	for object in model.objects.all():
		columns = ["<td>%s</td>" % getattr(object, field.name) for field in model._meta.fields]
		rows.append("<tr>%s</tr>" % "".join(columns))
	
	# dump it as a simple html table
	html = "<table>%s</table>" % "".join(rows)
	
	# download as an excel spreadsheet
	resp = http.HttpResponse(html, mimetype='application/vnd.ms-excel')
	resp["content-disposition"] = "attachment; filename=%s.xls" % model_name
	return resp

