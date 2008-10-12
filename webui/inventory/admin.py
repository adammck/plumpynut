from plumpynut.inventory.models import *
from django.contrib import admin

# add our models to the django admin
admin.site.register(Reporter)
admin.site.register(Supply)
admin.site.register(Location)
admin.site.register(SupplyLocation)

