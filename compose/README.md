# Chainlink :cloud: Compose

:octocat: Custom configuration of this deployment composition can be provided by setting environment variables of the operation environment explicitly:

`export API_USER=my-user`

or included within an environment config file located either at a `.env` file within the same directory or specified via the `env_vars` environment variable.

`export env_vars=/home/user/.chainlink/vars.env`

## Config


**Required**

| var | description |
| :---: | :---: |
| *API_USER* | Chainlink node operator http/s API username |
| *API_PASSWORD* | Chainlink node operator http/s API password |
| **..or..** *ADMIN_CREDENTIALS_FILE* | text file containing admin credentials (api username, password) for logging in |
| *OPERATOR_PASSWORD* | node operator password account |
| *POSTGRES_PASSWORD* | password to access required backend postgres database |

**Optional**

| var | description | default |
| :---: | :---: | :---: |
| *image* | Chainlink service container image to deploy | `0labs/chainlink:latest` |
| *SECURITY_OUTPUT_DIR* | directory within container to maintain secure credentials files | `/var/tmp/chainlink` |
| *SECURITY_CERT_DURATION* | TTL or duration (in days) prior to expiration for generated certs | `365` |
| *ui_port* | Chainlink node operation web UI service port | `6688` |
| *POSTGRES_USER* | username to access backend postgres database | `postgres` |
| *POSTGRES_HOST* | host address of backend postgres database | `postgres` |
| *POSTGRES_DB* | database name of backend postgres instance | `postgres` |
| *env_vars* | Path to environment file to load by compose Chainlink container (see [list](https://docs.chain.link/docs/configuration-variables/) of available config envvars) | `.env` |
| *host_data_dir* | host directory to store node runtime/operational data | `/var/tmp/chainlink` |
| *restart_policy* | container restart policy | `unless-stopped` |
| *postgres_image* | Postgres DB image to deploy | `postgres:latest` |
| *postgres_port* | Postgres DB container listening port | `5432` |

## Deploy examples

* Launch a Chainlink node connected to the Rinkeby Ethereum testnet:
```
# cat .env
SECURITY_OUTPUT_DIR=/mnt/secure
OPERATOR_PASSWORD=ABCabc123!@#$
API_USER=linknode@example.com
API_PASSWORD=passw0rd
ETH_CHAIN_ID=4
LINK_CONTRACT_ADDRESS=0x01BE23585060835E02B77ef475b0Cc51aA1e0709
ETH_URL=ws://ethereum-rpc.rinkeby.01labs.net:8546

docker-compose up
```

* Deploy non-default Chainlink node container image againt Ethereum mainnet with debug logging:
```
# cat .env
image=0labs/chainlink:0.10.13
OPERATOR_PASSWORD=ABCabc123!@#$
API_USER=linknode@example.com
API_PASSWORD=passw0rd
ETH_CHAIN_ID=1
ETH_URL=ws://ethereum-rpc.mainnet.01labs.net:8546
LOG_LEVEL=debug

docker-compose up -d  && docker-compose exec geth geth-helper status sync-progress
```

* Allow node API service to accept incoming requests for all interfaces and enable backup Ethereum nodes:
```
# cat .env
ALLOW_ORIGINS=*ETH_HTTP_URL
ETH_URL=ws://ethereum-rpc.mainnet.01labs.net:8546
ETH_HTTP_URL=http://ethereum-rpc.mainnet.01abs.net:8545
ETH_SECONDARY_URLS=https://mainnet.infura.io/v3/<YOUR-PROJECT-ID>,https://mainnet.rpc-backup:8545

docker-compose up
```

* Activate HTTPS connections to the API service and store generated certificates at custom host location:
```
# cat .env
ENABLE_HTTPS=true
SECURITY_OUTPUT_DIR=/chainlink/secure/
SECURITY_CERT_DURATION=30
sslmode=prefer

docker-compose up
```

* Connect to non-default Postres db instance with custom credentials:
```
# cat .env
POSTGRES_HOST=my-postgres.prod.instance
POSTGRES_DB=chainlink
POSTGRES_USER=my-user
POSTGRES_PASSWORD=topsecret

docker-compose up -d
```
