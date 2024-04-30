#FROM regd1.pslh.it:8443/dockerhubpsl/python:3.11-slim-bullseye
#FROM regd1.pslh.it:8443/dockerhubpsl/python:3.9-slim-bullseye
FROM python:3.9-slim-bullseye


# env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# the following ARG turns off the questions
# normally asked for location and timezone for Apache
ARG DEBIAN_FRONTEND=noninteractive

ADD ./assets_docker/ /

# set work directory
WORKDIR /rob_vhost

RUN apt-get -y update \
  && apt-get upgrade -y && apt-get clean -y \
  && apt-get -y --no-install-recommends install gawk  \
  && apt-get -y --no-install-recommends install openssl  \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && mkdir -p /var/www/hostings \
  && mkdir -p /var/log/apache2 \
  && mkdir -p /etc/apache2/sites-available

CMD ["/root/run.bash"]
