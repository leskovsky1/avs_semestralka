#!/bin/bash
echo "Hello world"
eval ifup eth0
eval git add .
eval git commit -m "Pokus"
eval git push origin master
eval ifdown eth0
