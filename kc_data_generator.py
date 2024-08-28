import requests
import json
from faker import Faker
import os

# Keycloak server details,
KEYCLOAK_URL = "http://localhost:8080/auth"
REALM = "master"
ADMIN_USER = os.environ["KEYCLOAK_ADMIN"]
ADMIN_PASSWORD = os.environ["KEYCLOAK_ADMIN_PASSWORD"]
CLIENT_ID = "admin-cli"

# New realm and clients configuration.
NEW_REALM_NAME = "test-realm"
CLIENTS = [
    {"clientId": "client1", "redirectUris": ["http://localhost:8080/*"]},
    {"clientId": "client2", "redirectUris": ["http://localhost:8081/*"]}
]

# Function to obtain an access token.
def get_admin_token():
    response = requests.post(
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "username": ADMIN_USER,
            "password": ADMIN_PASSWORD
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

# Function to create a new realm.
def create_realm(token, realm_name):
    response = requests.post(
        f"{KEYCLOAK_URL}/admin/realms",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "id": realm_name,
            "realm": realm_name,
            "enabled": True
        }
    )
    response.raise_for_status()
    print(f"Realm '{realm_name}' created.")

# Function to create clients.
def create_clients(token, realm_name, clients):
    for client in clients:
        response = requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/clients",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "clientId": client["clientId"],
                "redirectUris": client["redirectUris"],
                "enabled": True
            }
        )
        response.raise_for_status()
        print(f"Client '{client['clientId']}' created.")

# Function to create users.
def create_users(token, realm_name, num_users):
    for i in range(num_users):
        # Initialize a Faker instance.
        fake = Faker()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        username = f"{first_name.lower()}.{last_name.lower()}"
        response = requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/users",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "credentials": [{"type": "password", "value": "password123", "temporary": False}]
            }
        )
        response.raise_for_status()
        print(f"User '{username}' created.")

def main():
    try:
        token = get_admin_token()
        create_realm(token, NEW_REALM_NAME)
        create_clients(token, NEW_REALM_NAME, CLIENTS)
        create_users(token, NEW_REALM_NAME, 50)
        print("All resources created successfully.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
