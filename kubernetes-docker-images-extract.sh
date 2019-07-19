#!/bin/bash

if [ $# -lt 1 ]
then
cat << HELP

get-images.sh  --  list all Docker images found in a file

EXAMPLE: 
    -  ./get-images.sh kubernetes.yaml

HELP
fi

for file in "$@"
do
    cat $file | grep "image: " | awk '{ print $2 }'
done