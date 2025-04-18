import click
import os
from pathlib import Path
import os
from dotenv import load_dotenv

from cloaksmith.log import setup_logging, get_logger
from cloaksmith.auth import AuthSession
from cloaksmith.keycloak_roles import KeycloakClientRoleManager
from cloaksmith import __version__

log = get_logger()


def load_default_env():
    if os.name == "nt":
        config_path = Path(os.getenv("APPDATA")) / "cloaksmith" / ".env"
    else:
        config_path = Path.home() / ".config" / "cloaksmith" / ".env"

    if config_path.exists():
        load_dotenv(dotenv_path=config_path)
    else:
        log.warning(
            f"No .env file found at {config_path}. Please run 'cloaksmith init-env' to create one.")
        exit(1)


def load_env(ctx):
    env_file = ctx.obj.get("env_file")
    if env_file:
        load_dotenv(dotenv_path=env_file)
        log.info("Loaded environment variables from provided .env file.")
    else:
        load_default_env()
        log.info("Loaded environment variables from default .env file.")


@click.group()
@click.help_option("-h", "--help")
@click.version_option(__version__)
@click.option('--log-level', default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False), help="Set the log level")
@click.option('--env-file', type=click.Path(exists=True), help="Path to a .env file")
@click.pass_context
def cli(ctx, log_level, env_file):
    """
    A command-line interface for performing various Keycloak administration tasks.
    """
    setup_logging(log_level)
    ctx.obj = {"env_file": env_file}


@cli.command()
@click.help_option("-h", "--help")
def init_env():
    """
    Initialize a .env file in the appropriate config directory by prompting for values.
    """
    url = click.prompt(
        "KEYCLOAK_URL", prompt_suffix=" (e.g. https://your-keycloak/): ")
    realm = click.prompt(
        "KEYCLOAK_REALM", prompt_suffix=" (e.g. your-realm): ")
    client_id = click.prompt("KEYCLOAK_CLIENT_ID",
                             prompt_suffix=" (e.g. your-app-client-id): ")

    if os.name == "nt":
        config_dir = Path(os.getenv("APPDATA")) / "cloaksmith"
    else:
        config_dir = Path.home() / ".config" / "cloaksmith"
    config_dir.mkdir(parents=True, exist_ok=True)

    env_path = config_dir / ".env"
    with env_path.open("w") as f:
        f.write(f"KEYCLOAK_URL={url}\n")
        f.write(f"KEYCLOAK_REALM={realm}\n")
        f.write(f"KEYCLOAK_CLIENT_ID={client_id}\n")

    log.info(f".env file written to: {env_path}")


@cli.command()
@click.help_option("-h", "--help")
@click.argument("csv_path", type=click.Path(exists=True))
@click.option("--client-id", required=True, help="Target client ID")
@click.option("--realm", required=True, help="Target realm to modify")
@click.option("--no-cache", is_flag=True, help="Disable token caching")
@click.pass_context
def import_roles(ctx, csv_path, client_id, realm, no_cache):
    """
    Import roles and map them to groups using a CSV file.

    CSVPATH: Path to the CSV file containing role and group mappings.
    """
    load_env(ctx)

    base_url = os.getenv("KEYCLOAK_URL")
    login_realm = os.getenv("KEYCLOAK_REALM")
    client_id_env = os.getenv("KEYCLOAK_CLIENT_ID")

    auth = AuthSession(base_url=base_url, realm=login_realm,
                       client_id=client_id_env, no_cache=no_cache)
    auth.authenticate()

    kc = KeycloakClientRoleManager(auth, target_realm=realm)
    kc.import_roles_and_mappings(client_id, csv_path)


if __name__ == "__main__":
    cli()
