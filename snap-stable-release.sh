#!/bin/bash

# script to build snap
sudo snapcraft cleanbuild && \
snapcraft login && \
echo "enter snap file name: " && \
read snap && \
snapcraft push ${snap}
