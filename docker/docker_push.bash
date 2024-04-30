#!/bin/bash



TAG=$(cat tag)
sudo docker push psldocker/rob_vhost:${TAG}


