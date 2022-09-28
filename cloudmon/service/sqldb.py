# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import logging

import ansible_runner


class PostgreSQLManager:
    def __init__(self, cloudmon_config):
        self.config = cloudmon_config

    def provision(self, check):
        logging.info("Provisioning PostgreSQL")
        extravars = copy.deepcopy(self.config.default_extravars)
        extravars.update(
            dict(
                ansible_check_mode=check,
                postgresql_group_name="postgres",
                postgres_root_password=self.config.config["database"][
                    "root_password"
                ],
            )
        )
        r = ansible_runner.run(
            private_data_dir=self.config.private_data_dir,
            playbook="install_postgresql.yaml",
            inventory=self.config.inventory_path,
            extravars=extravars,
            verbosity=1,
        )
        if r.rc != 0:
            raise RuntimeError("Error Installing PostgreSQL")

        extravars.update(
            dict(
                ansible_check_mode=check,
                postgresql_group_name="postgres",
                postgres_root_password=self.config.config["database"][
                    "root_password"
                ],
                databases=self.config.config["database"]["databases"],
            )
        )

        r = ansible_runner.run(
            private_data_dir=self.config.private_data_dir,
            playbook="manage_databases.yaml",
            inventory=self.config.inventory_path,
            extravars=extravars,
            verbosity=1,
        )

        if r.rc != 0:
            raise RuntimeError("Error Configuring PostgreSQL databases")