#!/bin/bash
set -euo pipefail

# Print all commands executed if DEBUG mode enabled
[ -n "${DEBUG:-""}" ] && set -x

DIR=/docker-entrypoint.d

if [[ -d "$DIR" ]] ; then
  /bin/run-parts --exit-on-error "$DIR"
fi

# Update environment according to entrypoint logic
if [[ -f "${SECURITY_OUTPUT_DIR:-/var/tmp/chainlink}/.env" ]]; then
  source "${SECURITY_OUTPUT_DIR:-/var/tmp/chainlink}/.env" || true
fi

if [[ -n "${EXTRA_ARGS:-""}" ]]; then
  exec /usr/bin/tini -g -- $@ ${EXTRA_ARGS}
else
  exec /usr/bin/tini -g -- "$@"
fi
