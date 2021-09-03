#!/usr/bin/env python3

from datetime import datetime
import json
import os
import subprocess
import sys

import click
import requests

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    pass

@cli.group()
def status():
    pass

###
# Commands for application configuration customization and inspection
###

DEFAULT_API_ADDRESS = "http://localhost:6688"
DEFAULT_API_METHOD = "get"
DEFAULT_API_PARAMS = ""

def print_json(json_blob):
    print(json.dumps(json_blob, indent=4, sort_keys=True))

def execute_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode > 0:
        print('Executing command \"%s\" returned a non-zero status code %d' % (command, process.returncode))
        sys.exit(process.returncode)

    if error:
        print(error.decode('utf-8'))

    return output.decode('utf-8')

def execute_jsonrpc(rpc_address, method, params=[]):
    # prepare inputs for wire transfer
    for idx, item in enumerate(params):
        if item.lower() == "false":
            params[idx] = False
        elif item.lower() == "true":
            params[idx] == True

    req = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        result = requests.post(rpc_address, json=req, headers={'Content-Type': 'application/json'})
    except requests.exceptions.ConnectionError as err:
        return {
            "error": "Failed to establish connection to {rpc_addr} - {error}".format(
                rpc_addr=rpc_address,
                error=err
            )
        }

    if result.status_code == requests.codes.ok:
        return result.json()
    else:
        raise Exception("Bad Request: {res}".format(res=result))

@status.command()
@click.option('--api-addr',
              default=lambda: os.environ.get("API_ADDRESS", DEFAULT_API_ADDRESS),
              show_default=DEFAULT_API_ADDRESS,
              help='server address to query for API calls')
@click.option('--method',
              default=lambda: os.environ.get("API_METHOD", DEFAULT_API_METHOD),
              show_default=DEFAULT_API_METHOD,
              help='API HTTP method to execute a part of query')
@click.option('--params',
              default=lambda: os.environ.get("API_PARAMS", DEFAULT_API_PARAMS),
              show_default=DEFAULT_API_PARAMS,
              help='comma separated list of API query parameters')
def query_api(api_addr, method, params):
    """Execute API query
    """

    result = execute_jsonrpc(
        rpc_addr,
        method,
        params=[] if len(params) == 0 else params.split(',')
    )
    if 'error' in result:
        print_json(result['error'])
    else:
        print_json(result['result'])

if __name__ == "__main__":
    cli()
