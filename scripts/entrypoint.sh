#!/bin/bash
set -euo pipefail

# Print all commands executed if DEBUG mode enabled
[ -n "${DEBUG:-""}" ] && set -x

DIR=/docker-entrypoint.d

if [[ -d "$DIR" ]] ; then
  /bin/run-parts --exit-on-error "$DIR"
fi

# Update environment according to entrypoint logic
source "${SECURITY_OUTPUT_DIR:-/var/tmp/chainlink}/.env"

exec /usr/bin/tini -g -- "$@"