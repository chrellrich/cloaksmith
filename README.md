# Cloaksmith

Cloaksmith is a CLI tool designed to interact with a Keycloak server using OAuth 2.0 Device Authorization Grant. It allows you to import roles from a CSV file and create role mappings, with a focus on simplicity and extensibility.

## Prerequisites

- Python 3.7 or higher
- Keycloak server
- Keycloak client with OAuth 2.0 Device Authorization Grant enabled

## Installation

1. Clone the repository:

    ```shell
    git clone https://git.ellri.ch/c.ellrich/cloaksmith
    ```

2. Change to the project directory:

    ```shell
    cd cloaksmith
    ```

3. Install Cloaksmith using `pip`:

    ```shell
    pip install .
    ```

## Configuration

1. Create a Keycloak client with OAuth 2.0 Device Authorization Grant enabled. No other features are required. Refer to the Keycloak documentation for detailed instructions.

2. Initialize the configuration by running:

    ```shell
    cloaksmith init-env
    ```

     This will prompt you to enter the following values:

    - `KEYCLOAK_URL` (e.g. `https://your-keycloak/`)
    - `KEYCLOAK_REALM` (e.g. `master`)
    - `KEYCLOAK_CLIENT_ID` (e.g. `your-app-client-id`)

    The `.env` file will be saved to the appropriate config directory:

    - **Linux/macOS:** `~/.config/cloaksmith/.env`
    - **Windows:** `%APPDATA%\cloaksmith\.env`

3. Alternatively, you can specify a custom `.env` file using the `--env-file` option for any command:

    ```shell
    cloaksmith import-roles --env-file /path/to/.env ...
    ```

## Usage

Once installed, you can use the `cloaksmith` command to interact with your Keycloak server.

### General Help

To see the available commands and options, run:

```shell
cloaksmith --help
```

### Import Roles and Role Mappings to a Client

Create a CSV file based on the `role_mappings.csv.example` file provided.

Run the following command to import roles and map them to groups:

```shell
cloaksmith import-roles --client-id <target_client_id> --realm <target_client_realm> <path_to_csv>
```

## Extensibility
Cloaksmith is designed to be easily extensible. You can add new commands or functionality by modifying the CLI or the underlying modules.

## License
This project is licensed under the terms specified in the LICENSE file.