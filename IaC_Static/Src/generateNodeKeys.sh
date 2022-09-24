#!/bin/bash
ssh-keygen -q -N '' -t rsa -f Nodesstatic
ssh-keygen -q -N '' -t rsa -f Bastionstatic

mv Nodes Nodesstatic.privkey
mv Bastion Bastionstatic.privkey