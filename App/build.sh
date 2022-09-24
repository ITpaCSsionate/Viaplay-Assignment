#!/bin/bash

docker build -t 518606020119.dkr.ecr.eu-west-1.amazonaws.com/itpacssionate-pyappimage:v0.5 -f Docker/Dockerfile .
docker push 518606020119.dkr.ecr.eu-west-1.amazonaws.com/itpacssionate-pyappimage:v0.5

# docker run -p 8080:8080 --name pyapp -d 518606020119.dkr.ecr.eu-west-1.amazonaws.com/itpacssionate-pyappimage:v0.5


