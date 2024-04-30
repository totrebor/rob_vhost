#!/bin/bash



TAG=$(cat tag)
sudo docker run -it \
  --mount 'type=bind,src=./data/apache2,dst=/etc/apache2' \
  --mount 'type=bind,src=./data/apache2log,dst=/var/log/apache2' \
  --mount 'type=bind,src=./data/apache2www,dst=/var/www' \
  --mount 'type=bind,src=./data/vsftpd,dst=/etc/vsftpd' \
  --mount 'type=bind,src=./data/rob_vhost/config.json,dst=/etc/rob_vhost/config.json' \
  --mount 'type=bind,src=./data/rob_vhost/guest,dst=/etc/rob_vhost/guest' \
  psldocker/rob_vhost:${TAG} \
  /root/run.bash create

