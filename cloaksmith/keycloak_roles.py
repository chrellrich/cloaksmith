import csv
from cloaksmith.log import get_logger
log = get_logger()


class KeycloakClientRoleManager:
    def __init__(self, auth_session, target_realm):
        self.auth = auth_session
        self.target_realm = target_realm
        self.base_url = auth_session.base_url

    def get_client_id(self, client_id):
        url = f"{self.base_url}/admin/realms/{self.target_realm}/clients"
        res = self.auth.request("GET", url)
        clients = res.json()
        client = next((c for c in clients if c["clientId"] == client_id), None)
        if not client:
            log.error(
                f"Client '{client_id}' not found in realm '{self.target_realm}'")
            raise ValueError(
                f"Client '{client_id}' not found in realm '{self.target_realm}'")
        log.info(f"Found client ID for '{client_id}': {client['id']}")
        return client["id"]

    def create_role(self, client_internal_id, role_name):
        url = f"{self.base_url}/admin/realms/{self.target_realm}/clients/{client_internal_id}/roles"
        res = self.auth.request("POST", url, json={"name": role_name})
        if res.status_code not in (201, 409):
            log.error(f"Failed to create role '{role_name}': {res.text}")
            raise Exception(f"Failed to create role '{role_name}': {res.text}")
        log.info(f"Role '{role_name}' created successfully or already exists.")

    def get_role(self, client_internal_id, role_name):
        url = f"{self.base_url}/admin/realms/{self.target_realm}/clients/{client_internal_id}/roles/{role_name}"
        res = self.auth.request("GET", url)
        if res.status_code == 404:
            log.error(
                f"Role '{role_name}' not found in client '{client_internal_id}'")
            raise ValueError(f"Role '{role_name}' not found")
        log.info(f"Found role '{role_name}' in client '{client_internal_id}'")
        return res.json()

    def get_group_id(self, group_name):
        url = f"{self.base_url}/admin/realms/{self.target_realm}/groups"
        res = self.auth.request("GET", url)
        groups = res.json()
        group = next((g for g in groups if g["name"] == group_name), None)
        if not group:
            log.error(
                f"Group '{group_name}' not found in realm '{self.target_realm}'")
            raise ValueError(
                f"Group '{group_name}' not found in realm '{self.target_realm}'")
        log.info(f"Found group ID for '{group_name}': {group['id']}")
        return group["id"]

    def map_role_to_group(self, group_id, client_internal_id, role_obj):
        url = f"{self.base_url}/admin/realms/{self.target_realm}/groups/{group_id}/role-mappings/clients/{client_internal_id}"
        res = self.auth.request("POST", url, json=[role_obj])
        if res.status_code not in (204, 409):
            log.error(f"Failed to map role to group '{group_id}': {res.text}")
            raise Exception(f"Failed to map role to group: {res.text}")
        log.info(f"Role mapped to group '{group_id}' successfully.")

    def import_roles_and_mappings(self, client_id, csv_path):
        client_internal_id = self.get_client_id(client_id)
        failures = []

        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                role = row["role_name"]
                group = row["group_name"]
                log.info(f"Processing: Role='{role}' -> Group='{group}'")

                try:
                    self.create_role(client_internal_id, role)
                    group_id = self.get_group_id(group)
                    role_obj = self.get_role(client_internal_id, role)
                    self.map_role_to_group(
                        group_id, client_internal_id, role_obj)
                except Exception as e:
                    msg = f"Failed to process role '{role}' for group '{group}': {e}"
                    log.error(msg)
                    failures.append(msg)

        if failures:
            log.warning(f"Completed with {len(failures)} error(s).")
        else:
            log.info("Role cloning and mapping completed successfully.")
