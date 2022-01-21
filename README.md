<p><img src="https://avatars1.githubusercontent.com/u/12563465?s=200&v=4" alt="OCI logo" title="oci" align="left" height="70" /></p>
<p><img src="https://cryptomode.com/wp-content/uploads/2020/08/CryptoMode-chainLink-Price-696x392.jpg" alt="0xO1 logo" title="0xO1" align="right" height="100" /></p>

Container File 🔮🔗 Chainlink
=========
![GitHub release (latest by date)](https://img.shields.io/github/v/release/0x0I/container-file-chainlink?color=yellow)
[![0x0I](https://circleci.com/gh/0x0I/container-file-chainlink.svg?style=svg)](https://circleci.com/gh/0x0I/container-file-chainlink)
[![Docker Pulls](https://img.shields.io/docker/pulls/0labs/chainlink?style=flat)](https://hub.docker.com/repository/docker/0labs/chainlink)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)

Configure and operate Chainlink: a smart-contract platform data oracle network

**Overview**
  - [Setup](#setup)
    - [Build](#build)
    - [Config](#config)
  - [Operations](#operations)
  - [Examples](#examples)
  - [License](#license)
  - [Author Information](#author-information)

### Setup
--------------
Guidelines on running `0labs/chainlink` containers are available and organized according to the following software & machine provisioning stages:
* _build_
* _config_
* _operations_

#### Build

##### args

| Name  | description |
| ------------- | ------------- |
| `build_version` | base image to utilize for building application binaries/artifacts |
| `nvm_version` | version of the `nvm` tool to use for application builds |
| `node_version` | version of the `node` tool to use for application builds |
| `yarn_version` | version of the `yarn` tool to use for application builds |
| `chainlink_version` | `chainlink` application version to build within image |
| `goss_version` | `goss` testing tool version to install within image test target |
| `version` | container/image infra application version |

```bash
docker build --build-arg <arg>=<value> -t <tag> .
```

##### targets

| Name  | description |
| ------------- | ------------- |
| `builder` | image state following build of chainlink binary/artifacts |
| `test` | image containing test tools, functional test cases for validation and `release` target contents |
| `release` | minimal resultant image containing service binaries, entrypoints and helper scripts |
| `tool` | setup consisting of all chainlink utilities, helper tooling and `release` target contents |

```bash
docker build --target <target> -t <tag> .
```

#### Config

:page_with_curl: Configuration of the `chainlink` client can be expressed by exposing environment variables exported explicitly (**i.e.** `export ETH_CHAIN_ID=1`) or sourced from an environment var file to its runtime. A list of configurable settings can be found [here](https://docs.chain.link/docs/configuration-variables/).

_The following examples demonstrate exporting the aforementioned config envvars via *docker*'s supported methods:_

- container instance which explicitly exports individual environment config vars

  ```bash
  docker run --env ETH_CHAIN_ID=5 --env ETH_URL=ws://ethereum-rpc.goerli.01labs.net:8546 0labs/chainlink:latest 
  ```

- container instance loading `env` file consisting of a set of config environment variables

  ```bash
  cat .env
  ETH_CHAIN_ID=5
  ETH_URL=ws://ethereum-rpc.goerli.01labs.net:8546

  docker run --env-file .env 0labs/chainlink:latest 
  ```

`$EXTRA_ARGS=<string>` (**default**: `''`)
- space separated list of command-line flags to pass at run-time

  ```bash
  docker run --env EXTRA_ARGS="--debug" 0labs/chainlink:latest
  ```

_...and reference below for network/chain identification and communication configs:_ 

###### port mappings

| Port  | mapping description | type | config setting |
| :-------------: | :-------------: | :-------------: | :-------------: |
| `6688`    | Web UI server | *TCP*  | `CHAINLINK_PORT` |
| `6689`    | The port used for HTTPS connections. Set to 0 to disable HTTPS | *TLS*  | `CHAINLINK_TLS_PORT` |

###### chain id mappings

| name | config setting (ETH_CHAIN_ID) |
| :---: | :---: |
| Mainnet | 1 |
| Goerli | 5 |
| Kovan | 42 |
| Rinkeby | 4 |
| Ropsten | 3 |

see [chainlist.org](https://chainlist.org/) for a complete list

#### Operations

:flashlight: To assist with managing a `chainlink` client and interfacing with the *Chainlink Oracle* network, the following utility functions have been included within the image.

##### Setup security/admin credentials

Setup operator wallet and API credentials for secure access

```
$ chainlink-helper security setup-credentials --help
Usage: chainlink-helper security setup-credentials [OPTIONS]

  Setup operator wallet and API credentials for secure access

Options:
  --output-dir TEXT         directory to output security credential files
                            [default: (/var/tmp/chainlink)]
  --operator-password TEXT  password for chainlink node operator account
                            [default: (admin)]
  --api-user TEXT           password for chainlink node account  [default:
                            (linknode@example.com)]
  --api-password TEXT       password for chainlink node account  [default:
                            (admin)]
  --help                    Show this message and exit.
```

`$SECURITY_OUTPUT_DIR=</container/path>` (**default**: `/var/tmp/chainlink`)
- directory to output security credential files

`$API_USER=<email-address-format>` (**default**: `linknode@example.com`)
- api username for chainlink node account

`$API_PASSWORD=<string>` (**default**: `admin`)
- api password for chainlink node account

`$OPERATOR_PASSWORD=<string>` (**default**: `admin` **note:** must be changed to adhere to proper password format)
- password for chainlink node operator


API credentials and operator address password will be stored at `$SECURITY_OUTPUT_DIR` path as `.api` and `.password` files, respectively.

###### example

```bash
docker exec --env SECURITY_OUTPUT_DIR=/mnt --env API_USER=me@example.com --env API_PASSWORD=secret --env OPERATOR_PASSWORD=<chainlink-pwd-format> 0labs/chainlink:latest chainlink-helper security setup-credentials

cat /mnt/.api <(echo) /mnt/.password <(echo)
me@example.com
secret
<chainlink-pwd-format>
```

##### Generate TLS certs for HTTPS connections

Generate server TLS certificates for secure HTTPS API access

```
$ chainlink-helper security generate-certs --help
Usage: chainlink-helper security generate-certs [OPTIONS]

  Generate server certificates for secure HTTPS API access

Options:
  --output-dir TEXT     directory to output server certificates and keys
                        [default: (/var/tmp/chainlink)]
  --cert-duration TEXT  Days certificate should remain valid for  [default:
                        (365)]
  --help                Show this message and exit.
```

`$ENABLE_HTTPS=<bool>` (**default**: `false`)
- whether to automatically generate and store tls certs/keys on node startup

`$SECURITY_OUTPUT_DIR=</container/path>` (**default**: `/var/tmp/chainlink`)
- directory to output server certificates and keys

`$SECURITY_CERT_DURATION=</container/path>` (**default**: `365`)
- Days certificate should remain valid for

An HTTPS TLS certificate and key will be generated at `$SECURITY_OUTPUT_DIR` path as `server.crt` and `server.key`, respectively. Also, the appropriate
Chainlink TLS related environment variables (`TLS_CERT_PATH`, `TLS_KEY_PATH`, `SECURE_COOKIES`, `CHAINLINK_TLS_PORT`) will be set.

###### example

```bash
docker exec --env SECURITY_OUTPUT_DIR=/mnt --env SECURITY_CERT_DURATION=30 0labs/chainlink:latest chainlink-helper security generate-certs

ls /mnt/
server.crt
server.key

env
TLS_CERT_PATH=/mnt/server.crt
TLS_KEY_PATH=/mnt/server.key
SECURE_COOKIES=true
CHAINLINK_TLS_PORT=6689
```

##### Query HTTP/S API

Execute query against `chainlink`'s HTTP/S RESTful API server.

```
$ chainlink-helper status api-request --help
Usage: chainlink-helper status api-request [OPTIONS]

  Execute RESTful API HTTP request

Options:
  --host-addr TEXT     Chainlink API host address in format
                       <protocol(http/https)>://<IP>:<port>  [default:
                       (http://localhost:6688)]
  --api-user TEXT      user email for chainlink API node account  [default:
                       (linknode@example.com)]
  --api-password TEXT  password for chainlink API node account  [default:
                       (admin)]
  --api-method TEXT    HTTP method to execute a part of request  [default:
                       (GET)]
  --api-path TEXT      Restful API path to target resource  [default:
                       (v2/config)]
  --help               Show this message and exit.
```

`$API_HOST_ADDR=<web-address>` (**default**: `http://localhost:6688`)
- Chainlink API host address in format <protocol(http/https)>://<IP>:<port>

`$API_USER=<email-address-format>` (**default**: `linknode@example.com`)
- api username for chainlink node account

`$API_PASSWORD=<string>>` (**default**: `admin`)
- api password for chainlink node account

`$API_METHOD=<string>` (**default**: `GET`)
- HTTP method to execute a part of request

`$API_PATH=<string>` (**default**: `v2/config`)
- RESTful API path to target resource

The output consists of a JSON blob corresponding to the expected return object for a given API method. Reference [Chainlink's API wiki](https://github.com/smartcontractkit/chainlink/wiki/REST-API) for more details.

###### example

```bash
docker run --env API_HOST_ADDR=http://chainlink.mainnet.01labs.net --env API_METHOD=GET --env API_PATH=v2/keys/eth \
    0labs/chainlink:latest chainlink-helper status api-request

"data": [
        {
            "attributes": {
                "address": "0xd1aF1db4302756BADc4664a9D4DB6a1dF2de399C",
                "createdAt": "2021-09-19T22:30:15.752305Z",
                "deletedAt": null,
                "ethBalance": "2499776022999173456",
                "isFunding": false,
                "linkBalance": "120000000000000000000",
                "nextNonce": 0,
                "updatedAt": "2021-09-19T22:30:15.752305Z"
            },
            "id": "0xd1aF1db4302756BADc4664a9D4DB6a1dF2de399C",
            "type": "eTHKeys"
        }
    ]
}
```

Examples
----------------

* Set credentials and bind data/secure credentials directory to host path:
```
cat .env
SECURITY_OUTPUT_DIR=/chainlink/secure
API_USER=user
API_PASSWORD=secret
OPERATOR_PASSWORD=<secret>
DATABASE_URL=postgresql://postgres:secret@postgres:5432/postgres

docker run -it -v /mnt/chainlink/data:/chainlink --env-file .env 0labs/chainlink:latest chainlink node start -a /chainlink/secure/.api -p /chainlink/secure/.password
```

* Launch a Chainlink node targeting the Ethereum Rinkeby testnet:
```
cat .env
ETH_CHAIN_ID=4
LINK_CONTRACT_ADDRESS=0x01BE23585060835E02B77ef475b0Cc51aA1e0709
ETH_URL=ws://ethereum-rpc.rinkeby.01labs.net:8546

docker run --env--file .env 0labs/chainlink:latest
```

* Allow node API service to accept incoming requests for all interfaces and enable backup Ethereum nodes:
```
cat .env
ALLOW_ORIGINS=*
ETH_URL=ws://ethereum-rpc.mainnet.01labs.net:8546
ETH_HTTP_URL=http://ethereum-rpc.mainnet.01labs.net:8545
ETH_SECONDARY_URLS=https://mainnet.infura.io/v3/<YOUR-PROJECT-ID>,https://mainnet.rpc-backup:8545

docker run --env-file .env 0labs/chainlink:latest
```

* Activate HTTPS connections to the API service and store generated certificates at custom host location:
```
cat .env
ENABLE_HTTPS=true
SECURITY_OUTPUT_DIR=/chainlink/secure/
SECURITY_CERT_DURATION=30

docker run -v /mnt/secure:/chainlink/secure --env-file .env 0labs/chainlink:latest
```

* Connect to non-default Postres db instance with custom credentials:
```
cat .env
ETH_CHAIN_ID=1
DATABASE_URL=postgresql://ops:secret@postgres.prod.net:5432/chainlink
  
docker run --env-file .env 0labs/chainlink:latest
```

* Query Chainlink API of running node for service configuration:
```
cat .env
API_HOST_ADDR=http://chainlink-api.mainnet.01labs.net:6688
API_METHOD=GET
API_PATH=v2/config

docker exec --env-file .env chainlink chainlink-helper status api-request
```

License
-------

MIT

Author Information
------------------

This Containerfile was created in 2021 by O1.IO.

🏆 **always happy to help & donations are always welcome** 💸

* **ETH (Ethereum):** 0x652eD9d222eeA1Ad843efec01E60C29bF2CF6E4c

* **BTC (Bitcoin):** 3E8gMxwEnfAAWbvjoPVqSz6DvPfwQ1q8Jn

* **ATOM (Cosmos):** cosmos19vmcf5t68w6ug45mrwjyauh4ey99u9htrgqv09
