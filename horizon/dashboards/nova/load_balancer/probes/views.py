# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 OpenStack LLC
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django import shortcuts
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import tabs

from .forms import CreateProbe, CreateICMPProbe, CreateHTTPProbe
from .tabs import ProbeDetailTabs
from ..views import MultiTypeForm

from balancerclient.common import exceptions as balancerclient_exceptions


LOG = logging.getLogger(__name__)


class CreateView(MultiTypeForm):
    form_class = CreateProbe
    form_list = {'ICMP': CreateICMPProbe,
                 'HTTP': CreateHTTPProbe}
    template_name = 'nova/load_balancer/probes/create.html'

    def handle(self, request, data):
        probe_name = data.pop('name')
        probe_type = data.pop('type')
        try:
            api.probe_create(request, self.kwargs['lb_id'], probe_name,
                             probe_type, **data)
            message = "Creating probe \"%s\"" % (probe_name,)
            LOG.info(message)
            messages.success(request, message)
        except balancerclient_exceptions.ClientException, e:
            LOG.exception('ClientException in CreateProbe')
            messages.error(request,
                           _("Error Creating probe: %s") % e.message)
        return shortcuts.redirect('horizon:nova:load_balancer:detail',
                                  lb_id=self.kwargs['lb_id'])


class DetailView(tabs.TabView):
    tab_group_class = ProbeDetailTabs
    template_name = 'nova/load_balancer/probes/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["probe"] = self.get_data()
        return context

    def get_data(self):
        if not hasattr(self, "_probe"):
            lb_id = self.kwargs['lb_id']
            probe_id = self.kwargs['probe_id']
            try:
                probe = api.probe_get(self.request, lb_id, probe_id)
            except:
                redirect = urlresolvers.reverse(
                                   'horizon:nova:load_balancer:detail',
                                   args=(lb_id,))
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'Probe "%s".') % (probe_id,),
                                    redirect=redirect)
            self._probe = probe
        return self._probe

    def get_tabs(self, request, *args, **kwargs):
        probe = self.get_data()
        return self.tab_group_class(request, probe=probe, **kwargs)
