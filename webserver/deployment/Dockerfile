FROM python:3.9-buster

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends

# git clone
RUN git clone https://github.com/Isshwarya/crypto-ticker.git
WORKDIR /crypto-ticker/webserver/cryptoticker

# configure nginx
RUN cp /crypto-ticker/webserver/deployment/nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN chown -R www-data:www-data /crypto-ticker/webserver/cryptoticker

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/crypto-ticker/webserver/deployment/startup.sh"]