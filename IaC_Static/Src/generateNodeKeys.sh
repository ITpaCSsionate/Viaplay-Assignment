#!/bin/bash
ssh-keygen -q -N '' -t rsa -f Nodesstatic
ssh-keygen -q -N '' -t rsa -f Bastionstatic

mv Nodesstatic Nodesstatic.privkey
mv Bastionstatic Bastionstatic.privkey