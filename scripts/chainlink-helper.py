#!/usr/bin/env python3

import os
import sys

import click

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    pass

@cli.group()
def security():
    pass


DEFAULT_SECURITY_OUTPUT_DIR = "/var/tmp/chainlink"
DEFAULT_OPERATOR_PASSWORD = "admin"
DEFAULT_API_USER = "linknode"
DEFAULT_API_PASSWORD = "admin"


@security.command()
@click.option('--output-dir',
              default=lambda: os.environ.get("SECURITY_OUTPUT_DIR", DEFAULT_SECURITY_OUTPUT_DIR),
              show_default=DEFAULT_SECURITY_OUTPUT_DIR,
              help='directory to output security credential files')
@click.option('--operator-password',
              default=lambda: os.environ.get("OPERATOR_PASSWORD", DEFAULT_OPERATOR_PASSWORD),
              show_default=DEFAULT_OPERATOR_PASSWORD,
              help='password for chainlink node operator account')
@click.option('--api-user',
              default=lambda: os.environ.get("API_USER", DEFAULT_API_USER),
              show_default=DEFAULT_API_USER,
              help='password for chainlink node account')
@click.option('--api-password',
              default=lambda: os.environ.get("API_PASSWORD", DEFAULT_API_PASSWORD),
              show_default=DEFAULT_API_PASSWORD,
              help='password for chainlink node account')              
def setup_credentials(output_dir, operator_password, api_user, api_password):
    """
    Setup operator wallet and API credentials for secure access
    """

    admin_file = os.environ.get("ADMIN_CREDENTIALS_FILE")

    pwd_file = "{path}/.password".format(path=output_dir)
    api_file = "{path}/.api".format(path=output_dir)
    env_file = "{path}/.env".format(path=output_dir)
    if admin_file:
        if os.path.isfile(admin_file) or os.path.exists(admin_file):
            print("Admin credentials file path set but does not exist @{path}".format(path=admin_file))
    else:
        with open(api_file, 'w') as api_creds_file:
            api_creds_file.write("{user}\n{pwd}".format(user=api_user, pwd=api_password))

    if not (os.path.isfile(operator_password) or os.path.exists(operator_password)):
        with open(pwd_file, 'w') as operator_pwd_file:
            operator_pwd_file.write(operator_password)

    with open(env_file, 'w') as creds_env:
        extra_args = "{existing} -p {op_pwd_file}".format(existing=os.environ.get("EXTRA_ARGS", ""), op_pwd_file=pwd_file)
        creds_env.write("export ADMIN_CREDENTIALS_FILE={api}\nexport EXTRA_ARGS='{extra}'".format(api=api_file, extra=extra_args))


if __name__ == "__main__":
    cli()
