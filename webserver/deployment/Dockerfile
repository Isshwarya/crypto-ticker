FROM python:3.9-buster

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends

# Copy the workspace
# TODO: clone from git
RUN mkdir -p /food-menu-voting
ADD . /food-menu-voting
WORKDIR /food-menu-voting

# configure nginx
RUN cp /food-menu-voting/deployment/nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# Install dependencies
RUN pip install -r requirements.txt
RUN chown -R www-data:www-data /food-menu-voting

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/food-menu-voting/deployment/startup.sh"]