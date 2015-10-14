# Copyright 2015 Brocade Communications System, Inc.
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

from oslo_config import cfg

from tacker.tests import constants
from tacker.tests.functional.vnfd import base
from tacker.tests.utils import read_file

CONF = cfg.CONF


class VnfTestJSON(base.BaseTackerTest):
    def test_create_delete_vnf_monitoring(self):
        data = dict()
        data['tosca'] = read_file(
            'sample_vnfd_no_param_monitoring_respawn.yaml')
        toscal = data['tosca']
        tosca_arg = {'vnfd': {'attributes': {'vnfd': toscal}}}

        #Create vnfd with tosca template
        vnfd_instance = self.client.create_vnfd(body=tosca_arg)
        self.assertIsNotNone(vnfd_instance)

        ##Create vnf with vnfd_id
        vnfd_id = vnfd_instance['vnfd']['id']
        vnf_name = 'test_vnf_with_user_data_respawn'

        vnf_arg = {'vnf': {'vnfd_id': vnfd_id, 'name': vnf_name}}

        vnf_instance = self.client.create_vnf(body = vnf_arg)
        self.assertIsNotNone(vnf_instance)
        self.assertIsNotNone(vnf_instance['vnf']['id'])
        self.assertIsNotNone(vnf_instance['vnf']['instance_id'])
        self.assertEqual(vnf_instance['vnf']['vnfd_id'], vnfd_instance[
            'vnfd']['id'])

        ##Verify vnf is in ACTIVE state, then DEAD state and back ACTIVE again
        vnf_id = vnf_instance['vnf']['id']
        vnf_current_status = self.wait_until_vnf_active(vnf_id,
                                    constants.VNF_CIRROS_CREATE_TIMEOUT,
                                    constants.ACTIVE_SLEEP_TIME)

        self.assertEqual(vnf_current_status, 'ACTIVE')
        vnf_current_status = self.wait_until_vnf_dead(vnf_id,
                                    constants.VNF_CIRROS_DEAD_TIMEOUT,
                                    constants.DEAD_SLEEP_TIME)
        self.assertEqual(vnf_current_status, 'DEAD')
        vnf_current_status = self.wait_until_vnf_active(vnf_id,
                                    constants.VNF_CIRROS_CREATE_TIMEOUT,
                                    constants.ACTIVE_SLEEP_TIME)

        self.assertEqual(vnf_current_status, 'ACTIVE')

        ##Delete vnf_instance with vnf_id
        try:
            self.client.delete_vnf(vnf_id)
        except Exception:
            assert False, "vnf Delete failed after the monitor test"

        ##Delete vnfd_instance
        try:
            self.client.delete_vnfd(vnfd_id)
        except Exception:
            assert False, "vnfd Delete failed after the monitor test"
