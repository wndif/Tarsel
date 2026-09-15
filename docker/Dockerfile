# Tarsel2 — fault localization for Verilog.
#
# The image contains the Python tool plus the runtime libraries Synopsys VCS
# needs. It deliberately contains NO Synopsys executable, PLI archive or
# licence file: those stay in a private Docker volume the user provisions from
# an authorized installation, and are mounted read-only at run time.
#
#   docker volume create tarsel2_synopsys          # provision once (see README)
#   docker run --rm -v "$PWD:/data" \
#       -v tarsel2_synopsys:/opt/synopsys:ro \
#       -e LM_LICENSE_FILE=27000@<your-license-server> \
#       tarsel2:local localize --config examples/updown_counter/tarsel2.yaml
FROM ubuntu:20.04

# Docker forwards the host proxy into the build context; a socks5 proxy breaks
# apt/pip, so neutralise it. The container still reaches the network directly.
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG http_proxy
ARG https_proxy
ARG ALL_PROXY
ARG all_proxy
# Optional package index (for example a local mirror). Empty uses PyPI.
ARG PIP_INDEX_URL

RUN unset HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy no_proxy ALL_PROXY all_proxy \
    && apt-get -o Acquire::ForceIPv4=true update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get -o Acquire::ForceIPv4=true install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        csh \
        dc \
        file \
        libelf1 \
        libfontconfig1 \
        libncurses5 \
        libnuma1 \
        libtinfo5 \
        libx11-6 \
        libxext6 \
        libxft2 \
        libxi6 \
        libxrender1 \
        libxtst6 \
        make \
        perl \
        procps \
        python3 \
        python3-pip \
        tcsh \
        zlib1g \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sfn bash /bin/sh

COPY pyproject.toml README.md /src/
COPY src/ /src/src/
# Same proxy neutralisation as above: a forwarded socks5 proxy breaks pip.
RUN unset HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy no_proxy ALL_PROXY all_proxy \
    && python3 -m pip install --no-cache-dir \
        ${PIP_INDEX_URL:+--index-url "$PIP_INDEX_URL"} /src

# Overridable defaults matching the volume layout documented in the README.
ENV VCS_HOME=/opt/synopsys/vcs/O-2018.09-SP2
ENV PATH="/opt/synopsys/vcs/O-2018.09-SP2/bin:/usr/local/bin:/usr/bin:/bin"

WORKDIR /data
ENTRYPOINT ["tarsel2"]
CMD ["--help"]
