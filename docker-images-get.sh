#!/bin/bash
# https://stackoverflow.com/questions/35575674/how-to-save-all-docker-images-and-copy-to-another-machine


REGISTRY=harbor.dev.gov.sg
REGISTRY_PATH=/library

if [ $# -lt 1 ]
then
cat << HELP

docker-grab-images.sh  --  Get/Put all docker images in images.list

EXAMPLE: 
    - Get docker images to tar file:
       docker-grab-images.sh pull

    - Push docker images from tar file:
       docker-grab-images.sh push

    - Clean up:
       docker-grab-images.sh clean

HELP
fi

if [ "$1" == "pull" ]
then
# pull images from internet
cat images.list | xargs -L1 docker pull
docker images

DATE=`date --iso-8601=seconds`

# save to one big tar file
#docker save $(docker images -q) -o ./docker-images-$DATE.tar

# Save image meta
docker images | sed '1d' | awk '{print $1 " " $2 " " $3}' > docker-images-meta-$DATE.list
fi 

if [ "$1" == "push" ]
then
# load from tar file to host images
#docker load -i ./docker-images-*.tar
docker images

# tag all images
while read REPOSITORY TAG IMAGE_ID
do
        echo "== Tagging $REPOSITORY $TAG $IMAGE_ID =="
        docker tag "$IMAGE_ID" "$REGISTRY$REGISTRY_PATH/${REPOSITORY##*/}:$TAG"
        docker push "$REGISTRY$REGISTRY_PATH/${REPOSITORY##*/}:$TAG"
done <  docker-images-meta*.list
docker images
fi

if [ "$1" == "clean" ]
then
# clean up all files
rm docker-images-meta-*.list
rm docker-images-*.tar

# remove images
docker rmi -f $(docker images -a -q)
docker images
fi
