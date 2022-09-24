#!/bin/bash
ssh-keygen -q -N '' -t rsa -f Nodes
ssh-keygen -q -N '' -t rsa -f Bastion

mv Nodes Nodes.privkey
mv Bastion Bastion.privkey