#!/bin/sh
echo "update upgrade"
sudo apt-get update -y && \
sudo apt-get upgrade -y && \

echo "install gcc-7"
sudo apt-get install build-essential software-properties-common -y && \
sudo add-apt-repository ppa:ubuntu-toolchain-r/test -y && \
sudo apt-get update -y && \
sudo apt-get install gcc-7 g++-7 -y && \
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 60 --slave /usr/bin/g++ g++ /usr/bin/g++-7 && \
sudo update-alternatives --config gcc && \

echo "install git"
sudo apt-get install git

echo "install mongo"
sudo apt -y install mongodb wget git && \
sudo systemctl start mongodb

echo "install go"
sudo chown -R ubuntu /home/ubuntu/test/ && \
cd /home/ubuntu/test && \
wget https://dl.google.com/go/go1.12.9.linux-amd64.tar.gz && \
sudo tar -C /usr/local -zxvf go1.12.9.linux-amd64.tar.gz && \

echo "export GOPATH to bashrc"
echo $HOME
echo 'export HOME=/home/ubuntu' >> /home/ubuntu/.bashrc
echo 'export GOPATH=$HOME/go' >> /home/ubuntu/.bashrc
echo 'export GOROOT=/usr/local/go' >> /home/ubuntu/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin:$GOROOT/bin' >> /home/ubuntu/.bashrc
echo 'export GO111MODULE=off' >> /home/ubuntu/.bashrc
. /home/ubuntu/.bashrc

echo "Download go.tar.gz"
cd /home/ubuntu
CONFIRM=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate "https://docs.google.com/uc?export=download&id=1YdiOewHyrtylvpSriS_ZgaAwn6zXk7p2" -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$CONFIRM&id=1YdiOewHyrtylvpSriS_ZgaAwn6zXk7p2" -O go.tar.gz
rm -rf /tmp/cookies.txt
echo "Download go.tar.gz finish"

echo "tar free5gc"
cd /home/ubuntu
tar -C /home/ubuntu/ -zxvf go.tar.gz

echo "export GOPATH for bash shell"
export HOME=/home/ubuntu
export GOPATH=$HOME/go
export GOROOT=/usr/local/go
export PATH=$PATH:$GOPATH/bin:$GOROOT/bin
export GO111MODULE=off

echo "tar free5gc_libs"
cd /home/ubuntu/go/src/free5gc
tar -C /home/ubuntu/go -zxvf free5gc_libs.tar.gz

echo "configure NRF"
cat > /home/ubuntu/src/free5gc/config/nrfcfg.conf <<- EOM
info:
  version: 1.0.0
  description: NRF initial local configuration

configuration:
  MongoDBName: "free5gc"
  MongoDBUrl: "mongodb://172.24.4.110:27017"
  DefaultServiceIP: 172.24.4.101
  sbi:
    scheme: https
    ipv4Addr: 172.24.4.101
    port: 29510
  DefaultPlmnId:
    mcc: "208"
    mnc: "93"
  serviceNameList:
    - nnrf-nfm
    - nnrf-disc
EOM

echo "initialize NRF"
go build -o bin/nrf -x src/nrf/nrf.go

echo "run NRF"
sudo ./bin/nrf

