# ----------- STAGE 1: Builder --------------------
FROM python:3.13-slim-bookworm AS builder
LABEL maintainer="Terry Brooks, Jr."

# ----------- STAGE 1: Builder --------------------
FROM python:3.13-slim-bookworm AS builder
LABEL maintainer="Terry Brooks, Jr."

ARG TOKEN

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app:${PATH}" \
    MYSQLCLIENT_LDFLAGS="" \
    MYSQLCLIENT_CFLAGS=""

# Install build dependencies
    MYSQLCLIENT_CFLAGS=""

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cargo \
    curl \
    default-libmysqlclient-dev \
    git \
    libbz2-dev \
    libffi-dev \
    libffi-dev \
    liblzma-dev \
    libncurses5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    pkg-config \
    rustc \
    wget \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pip tools & dependencies
RUN pip install --upgrade pip setuptools wheel

# Install Python packages (including mysqlclient)
COPY requirements/dev.txt /tmp/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install --no-cache-dir -r /tmp/dev.txt \
    && pip install --prefix=/install mysqlclient==2.2.7 --global-option=build_ext \
    --global-option="-I/usr/include/mysql" \
    --global-option="-L/usr/lib/x86_64-linux-gnu" \
    --global-option="-lmysqlclient"




# ----------- STAGE 2: Runtime --------------------
FROM python:3.13-slim-bookworm

ENV PATH="/install/bin:/app:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOPPLER_CONFIG=dev \
    DOPPLER_PROJECT=little_lemon \
    DB_CERT_PATH=/app/AIVEN_SSL.pem \
    DOPPLER_TOKEN=${DOPPLER_TOKEN} 

# Install minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    default-libmysqlclient-dev \
    libffi-dev \
    libssl-dev \
    micro \
    nodejs \
    npm \
    supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python site-packages and binaries from builder
COPY --from=builder /install /usr/local

# Copy app files and SSL cert
WORKDIR /app
COPY --chown=1000:1000 AIVEN.pem /app/AIVEN_SSL.pem
COPY --chown=1000:1000 . /app/


# Copy Doppler CLI install script
RUN curl -sLf --retry 3 --tlsv1.2 --proto "=https" https://packages.doppler.com/public/cli/install.sh | sh -s -- --no-install-cli-version-file --install-path /install/bin
# Install Task binary
RUN curl -sSL https://taskfile.dev/install.sh | sh -s -- -d -b /install/bin
# Create non-root user
RUN groupadd -r appuser && useradd -m -r -g appuser appuser
USER appuser

ENTRYPOINT ["/bin/bash"]
CMD ["task", "serve"]