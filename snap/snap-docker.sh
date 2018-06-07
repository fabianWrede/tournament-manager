#!/bin/bash

cd .. && \
sudo docker run -v $(pwd):/tournament-manager snapcore/snapcraft sh -c "apt update && cd /tournament-manager && snapcraft" 
