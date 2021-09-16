#!/usr/bin/env python3

import json
import os
import sys
import subprocess

import click
import pickle
import requests

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    pass

@cli.group()
def security():
    pass

@cli.group()
def status():
    pass


DEFAULT_SECURITY_OUTPUT_DIR = '/var/tmp/chainlink'
DEFAULT_SECURITY_CERT_DURATION = '365'
DEFAULT_OPERATOR_PASSWORD = 'admin'
DEFAULT_API_HOST_ADDR = 'http://localhost:6688'
DEFAULT_API_METHOD = 'GET'
DEFAULT_API_PATH = 'v2/config'
DEFAULT_API_USER = 'linknode@example.com'
DEFAULT_API_PASSWORD = 'admin'
DEFAULT_API_COOKIE_FILE = '/tmp/cookiefile'


def print_json(json_blob):
    print(json.dumps(json_blob, indent=4, sort_keys=True))

def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def execute_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode > 0:
        print('Executing command \"%s\" returned a non-zero status code %d' % (command, process.returncode))
        sys.exit(process.returncode)

    if error:
        print(error.decode('utf-8'))

    return output.decode('utf-8')


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

    with open(env_file, 'a') as creds_env:
        creds_env.write("export ADMIN_CREDENTIALS_FILE={api}\n".format(api=api_file))

@security.command()
@click.option('--output-dir',
              default=lambda: os.environ.get("SECURITY_OUTPUT_DIR", DEFAULT_SECURITY_OUTPUT_DIR),
              show_default=DEFAULT_SECURITY_OUTPUT_DIR,
              help='directory to output server certificates and keys')
@click.option('--cert-duration',
              default=lambda: os.environ.get("SECURITY_CERT_DURATION", DEFAULT_SECURITY_CERT_DURATION),
              show_default=DEFAULT_SECURITY_CERT_DURATION,
              help='Days certificate should remain valid for')
def generate_certs(output_dir, cert_duration):
    """
    Generate server certificates for secure HTTPS API access
    """

    execute_command("mkdir -p {dir}".format(dir=output_dir))

    ssl_config_file = "{dir}/ssl-config".format(dir=output_dir)
    with open(ssl_config_file, 'w') as ssl_config:
        ssl_config.write("[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")
    ret = execute_command(
        "openssl req -x509 -out {dir}/server.crt  -keyout {dir}/server.key -newkey rsa:2048 -nodes -sha256 -days {duration} \
        -subj /CN=localhost -extensions EXT -config {dir}/ssl-config".format(dir=output_dir, duration=cert_duration)
    )

    env_file = "{dir}/.env".format(dir=output_dir)
    with open(env_file, 'a') as creds_env:
        creds_env.write(
            "export TLS_CERT_PATH={dir}/server.crt\nexport TLS_KEY_PATH={dir}/server.key\nexport SECURE_COOKIES=true\nexport CHAINLINK_TLS_PORT=".format(dir=output_dir)
        )

@status.command()
@click.option('--host-addr',
              default=lambda: os.environ.get("API_HOST_ADDR", DEFAULT_API_HOST_ADDR),
              show_default=DEFAULT_API_HOST_ADDR,
              help='Chainlink API host address in format <protocol(http/https)>://<IP>:<port>')
@click.option('--api-user',
              default=lambda: os.environ.get("API_USER", DEFAULT_API_USER),
              show_default=DEFAULT_API_USER,
              help='user email for chainlink API node account')
@click.option('--api-password',
              default=lambda: os.environ.get("API_PASSWORD", DEFAULT_API_PASSWORD),
              show_default=DEFAULT_API_PASSWORD,
              help='password for chainlink API node account')
@click.option('--api-method',
              default=lambda: os.environ.get("API_METHOD", DEFAULT_API_METHOD),
              show_default=DEFAULT_API_METHOD,
              help='HTTP method to execute a part of request')
@click.option('--api-path',
              default=lambda: os.environ.get("API_PATH", DEFAULT_API_PATH),
              show_default=DEFAULT_API_PATH,
              help='Restful API path to target resource')
@click.option('--cookie-file',
              default=lambda: os.environ.get("API_COOKIE_FILE", DEFAULT_API_COOKIE_FILE),
              show_default=DEFAULT_API_COOKIE_FILE,
              help='path of cookie file to load for API requests')
def api_request(host_addr, api_user, api_password, api_method, api_path, cookie_file):
    """
    Execute RESTful API HTTP request
    """

    data = {
        "email": api_user,
        "password": api_password
    }
    resp = requests.post("{host}/sessions".format(host=host_addr), json=data, headers={'Content-Type': 'application/json'})
    save_cookies(resp.cookies, cookie_file)

    c = load_cookies(cookie_file)
    try:
        if api_method.upper() == "POST":
            resp = requests.post("{host}/{path}".format(host=host_addr, path=api_path), cookies=c)
        else:
            resp = requests.get("{host}/{path}".format(host=host_addr, path=api_path), cookies=c)
    except requests.exceptions.ConnectionError as err:
        return {
            "error": "Failed to establish connection to {host} - {error}".format(
                host=host_addr,
                error=err
            )
        }

    print_json(resp.json())


if __name__ == "__main__":
    cli()
