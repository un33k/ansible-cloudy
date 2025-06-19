FROM debian:bookworm-slim

LABEL maintainer="ansible-cloudy"
LABEL description="Base Debian container for server deployments"

# Install essential packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        gnupg \
        lsb-release \
        apt-transport-https \
        software-properties-common \
        sudo \
        openssh-server \
        systemd \
        systemd-sysv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure systemd
RUN systemctl set-default multi-user.target

# Create non-root user
RUN useradd -m -s /bin/bash -G sudo deploy && \
    echo 'deploy ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/deploy

# SSH configuration
RUN mkdir /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

USER deploy
WORKDIR /home/deploy

EXPOSE 22

CMD ["/lib/systemd/systemd"]