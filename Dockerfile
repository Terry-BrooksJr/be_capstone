FROM python :3.13-slim
LABEL "maintainer"="Terry Brooks, Jr."
LABEL "description"="Containerized Little Lemon application with Python 3.13, MySQL, and Doppler CLI"
LABEL "version"="1.0"
LABEL "repository"="https://github.com/Terry-BrooksJr/be_capstone"
ARG TOKEN

# Set noninteractive installation
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app:${PATH}" \
    DOPPLER_TOKEN=${TOKEN} \
    MYSQLCLIENT_LDFLAGS="" \
    MYSQLCLIENT_CFLAGS="" \
    DB_CERT_PATH=/app/AIVEN_SSL.pem \
    DOPPLER_CONFIG=dev \
    DOPPLER_PROJECT=little_lemon 
    
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cargo \
    curl \
    default-libmysqlclient-dev \
    git \
    gnupg \
    libbz2-dev \
    libffi-dev \ 
    nodejs \
    npm \
    liblzma-dev \
    libncurses5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    lsb-release \
    micro \
    mysql-server \
    pkg-config \
    rustc \
    software-properties-common \
    wget \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Doppler CLI
RUN curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" > /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && apt-get install -y --no-install-recommends doppler && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    doppler setup --no-interactive


# # Install Python 3.13
# RUN wget -q https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz -P /tmp && \
#     tar -xzf /tmp/Python-3.13.0.tgz -C /tmp && \
#     cd /tmp/Python-3.13.0 && ./configure --enable-optimizations && make -j "$(nproc)" && make altinstall && \
#     rm -rf /tmp/Python-3.13.0 /tmp/Python-3.13.0.tgz

# # Create symbolic links for python and pip
# RUN ln -sf /usr/local/bin/python3.13 /usr/local/bin/python3 && \
#     ln -sf /usr/local/bin/python3.13 /usr/local/bin/python && \
#     ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip3 && \
#     ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip

# Upgrade pip
RUN pip install --upgrade pip

# Install Task (https://taskfile.dev)
RUN curl -sSL https://taskfile.dev/install.sh | sh -s -- -d -b /usr/local/bin

# Install mysqlclient dependencies and Python dependencies
RUN pip install wheel setuptools && \
    pip install mysqlclient==2.2.7 --global-option=build_ext \
    --global-option="-I/usr/include/mysql" \
    --global-option="-L/usr/lib/aarch64-linux-gnu" \
    --global-option="-lmysqlclient"

# Copy requirements files and install dependencies
COPY requirements/base.txt requirements/dev.txt /tmp/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r /tmp/base.txt && \
    pip install --no-cache-dir -r /tmp/dev.txt

WORKDIR /app

# Create a user and set up sudo access
RUN groupadd -r appuser && useradd -m -r -g appuser appuser && \
    mkdir -p /etc/sudoers.d && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/appuser && \
    chmod 440 /etc/sudoers.d/appuser
COPY --chown=appuser:appuser AIVEN_SSL.pem /app/AIVEN_SSL.pem
COPY . /app/
# Switch to the user
USER appuser


# Set entrypoint and command
ENTRYPOINT ["/bin/bash"]
CMD ["task", "serve"]