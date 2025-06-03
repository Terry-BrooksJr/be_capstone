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
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cargo \
    curl \
    default-libmysqlclient-dev \
    git \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncurses5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    pkg-config \
    ca-certificates \
    rustc \
    wget \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pip tools & Poetry
RUN pip install --upgrade pip setuptools wheel
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.2
ENV PATH="/root/.local/bin:$PATH"

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Copy only the dependency files first for better caching
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install Python packages
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    # Export dependencies to requirements.txt using Poetry
    poetry export --without-hashes -f requirements.txt > /tmp/requirements.txt && \
    # Install pip/setuptools/wheel to ensure they're not removed
    pip install --prefix=/install --no-cache-dir pip setuptools wheel && \
    # Install the dependencies from the exported requirements file
    pip install --prefix=/install --no-cache-dir -r /tmp/requirements.txt && \
    # Install mysqlclient with the required build flags
    MYSQLCLIENT_CFLAGS="-I/usr/include/mysql" \
    MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient" \
    pip install --prefix=/install mysqlclient==2.2.7



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

# Set shell options for safer execution  
SHELL ["/bin/bash", "-o", "pipefail", "-c"] 

# Copy Doppler CLI install script
RUN (curl -sLf --retry 3 --tlsv1.2 --proto "=https" https://packages.doppler.com/public/cli/install.sh) | sh -s -- --no-install-cli-version-file --install-path /install/bin
# Install Task binary
RUN RUN set -o pipefail && \ 
    curl -sSL https://taskfile.dev/install.sh | sh -s -- -d -b /install/bin
EXPOSE 7575
# Create non-root user
RUN groupadd -r appuser && useradd -m -r -g appuser appuser
USER appuser
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \  
    CMD curl -f http://localhost:7575/checkup || exit 1 
# Set the entrypoint to run gunicorn directly (matching what task:serve does)
ENTRYPOINT ["gunicorn"]
CMD ["--bind", ":7575", "--workers=2", "--threads=2", "config.wsgi:application"]
