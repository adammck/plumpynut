#!/usr/bin/env python
# vim: noet

from django.core.management import setup_environ
from webui import settings
setup_environ(settings)

from webui.inventory import models

from webui.inventory.views import refresh_graphs
refresh_graphs()
