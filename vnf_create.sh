#!/bin/bash

#openstack vnf create --vnfd-name mongo mongo --vim-name jefferyvim --description "mongodb"
openstack vnf create --vnfd-name upf1 upf1 --vim-name jefferyvim --description "upf1"
openstack vnf create --vnfd-name upf2 upf2 --vim-name jefferyvim --description "upf2"
openstack vnf create --vnfd-name upf3 upf3 --vim-name jefferyvim --description "upf3"

sleep 10

openstack vnf create --vnfd-name nrf nrf --vim-name jefferyvim --description "nrf"
sleep 10
openstack vnf create --vnfd-name amf amf --vim-name jefferyvim --description "amf"
sleep 10
openstack vnf create --vnfd-name smf smf --vim-name jefferyvim --description "smf"
sleep 10
openstack vnf create --vnfd-name udr udr --vim-name jefferyvim --description "udr"
sleep 10
openstack vnf create --vnfd-name pcf pcf --vim-name jefferyvim --description "pcf"
sleep 10
openstack vnf create --vnfd-name udm udm --vim-name jefferyvim --description "udm"
sleep 10
openstack vnf create --vnfd-name nssf nssf --vim-name jefferyvim --description "nssf"
sleep 10
openstack vnf create --vnfd-name ausf ausf --vim-name jefferyvim --description "ausf"

