ARG build_version="golang:1.16-stretch"

# ******* Stage: builder ******* #
FROM ${build_version} as builder

ARG nvm_version=v0.38.0
ARG node_version=v12.18
ARG yarn_version=1.22.11
ARG chainlink_version=v0.10.13

RUN apt update && apt install --yes --no-install-recommends git make curl jq

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/${nvm_version}/install.sh | bash
RUN . ~/.bashrc && nvm install ${node_version} && nvm use ${node_version} && npm install yarn@${yarn_version} --global

WORKDIR /tmp
RUN git clone --depth 1 --branch ${chainlink_version} https://github.com/smartcontractkit/chainlink
RUN cd chainlink && . ~/.bashrc && make install

# ******* Stage: base ******* #
FROM ubuntu:20.04 as base

RUN apt update && apt install --yes --no-install-recommends \
    ca-certificates \
    curl \
    pip \
    tini \
    # apt cleanup
	&& apt-get autoremove -y; \
	apt-get clean; \
	update-ca-certificates; \
	rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

WORKDIR /docker-entrypoint.d
COPY entrypoints /docker-entrypoint.d
COPY scripts/entrypoint.sh /usr/local/bin/chainlink-entrypoint

COPY scripts/chainlink-helper.py /usr/local/bin/chainlink-helper
RUN chmod 775 /usr/local/bin/chainlink-helper

RUN pip install click requests

ENTRYPOINT ["chainlink-entrypoint"]

# ******* Stage: testing ******* #
FROM base as test

ARG goss_version=v0.3.16

RUN curl -fsSL https://goss.rocks/install | GOSS_VER=${goss_version} GOSS_DST=/usr/local/bin sh

WORKDIR /test

COPY test /test
COPY --from=builder /go/bin/chainlink /usr/local/bin/

CMD ["goss", "--gossfile", "/test/goss.yaml", "validate"]

# ******* Stage: release ******* #
FROM base as release

ARG version=0.1.0

LABEL 01labs.image.authors="zer0ne.io.x@gmail.com" \
	01labs.image.vendor="O1 Labs" \
	01labs.image.title="0labs/chainlink" \
	01labs.image.description="Chainlink node of the decentralized oracle network, bridging on and off-chain computation." \
	01labs.image.source="https://github.com/0x0I/container-file-chainlink/blob/${version}/Dockerfile" \
	01labs.image.documentation="https://github.com/0x0I/container-file-chainlink/blob/${version}/README.md" \
	01labs.image.version="${version}"

COPY --from=builder /go/bin/chainlink /usr/local/bin/

#      app   ssl
#       ↓     ↓
EXPOSE 6688 6689

CMD ["chainlink", "node", "start"]

# ******* Stage: tools ******* #

FROM builder as build-tools

RUN cd /tmp/chainlink && . ~/.bashrc && make abigen

# ------- #

FROM base as tools

COPY --from=build-tools /go/bin/* /usr/local/bin/

WORKDIR /root/

CMD ["/bin/bash"]
