# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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

"""
Views for Instances and Volumes.
"""
import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tables
from horizon import forms

from .tables import LoadBalancersTable
from .forms import CreateForm, UpdateForm


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = LoadBalancersTable
    template_name = 'nova/load_balancer/index.html'

    def get_data(self):
        LOG.debug("Retrieve loadbalancers list %r" % self.request)
        try:
            lbs = api.lb_list(self.request)
        except:
            lbs = []
            exceptions.handle(self.request,
                    _('Unable to retrieve load balancers information.'))
        return lbs


class CreateView(forms.ModalFormView):
    form_class = CreateForm
    template_name = 'nova/load_balancer/create.html'


class UpdateView(forms.ModalFormView):
    form_class = UpdateForm
    template_name = 'nova/load_balancer/update.html'
    context_object_name = 'lb'

    def get_object(self, *args, **kwargs):
        if not hasattr(self, 'object'):
            lb_id = self.kwargs['lb_id']
            try:
                self.object = api.lb_get(self.request, lb_id)
            except:
                redirect = reverse("horizon:nova:load_balancer:index")
                msg = _('Unable to retrieve load balancer details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self.object

    def get_initial(self):
        return {'lb': self.kwargs['lb_id'],
                'name': self.object.name,
                'algorithm': self.object.algorithm,
                'port': getattr(self.object, 'port', '')}