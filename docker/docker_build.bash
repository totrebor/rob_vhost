#!/bin/bash



TAG=$(cat tag)
#./docker_prepare.bash
sudo docker build -t psldocker/rob_vhost:${TAG} .


