FROM ansible-cloudy/debian-base:latest

LABEL description="Web server container with Nginx and PHP-FPM"

USER root

# Install web server packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nginx \
        php8.2-fpm \
        php8.2-cli \
        php8.2-common \
        php8.2-mysql \
        php8.2-redis \
        php8.2-curl \
        php8.2-json \
        php8.2-mbstring \
        php8.2-xml \
        php8.2-zip \
        php8.2-gd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure Nginx
RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Configure PHP-FPM
RUN sed -i 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' /etc/php/8.2/fpm/php.ini

# Create web directory
RUN mkdir -p /var/www/html && \
    chown -R www-data:www-data /var/www/html

USER deploy
WORKDIR /var/www/html

EXPOSE 80 443

CMD ["/lib/systemd/systemd"]