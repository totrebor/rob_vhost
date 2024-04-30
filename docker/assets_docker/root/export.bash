#!/bin/bash


# copy default configurations files to /export

# clean
rm -r /export/etc 2>/dev/null

# copy
mkdir /export/etc
cp -rpd /etc/rob_vhost /export/etc/rob_vhost

