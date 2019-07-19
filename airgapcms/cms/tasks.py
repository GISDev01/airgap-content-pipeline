from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

from .models import DockerImage
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists)

import docker
import os
from pathlib import Path

from urllib.request import urlopen
from bs4 import BeautifulSoup

from npmdownloader import NpmPackageDownloader, MultiPackageDownloader
import tarfile

import time

logger = get_task_logger(__name__)

docker_image_path = "/mnt/c/Users/kyh/Code/airgap-content-pipeline/temp_files/docker/"
docker_bucket_name = "docker"

npm_path = "/mnt/c/Users/kyh/Code/airgap-content-pipeline/temp_files/npm/packages/"
npm_bucket_name = "npm"

def tardir(path, tar_name):
    with tarfile.open(tar_name, "w:gz") as tar_handle:
        for root, dirs, files in os.walk(path):
            for file in files:
                tar_handle.add(os.path.join(root, file))

#@periodic_task(
#    run_every=(crontab(minute='*/2')),
#    name="task_download_docker_images",
#    ignore_result=True
#)

def task_download_docker_images():
    download_list =  DockerImage.objects.all()
    dockerClient = docker.from_env()
    localMinioClient = Minio('127.0.0.1:9000',
        access_key=os.getenv('LOCAL_MINIO_ACCESS_KEY', 'Token Not found'),
        secret_key=os.getenv('LOCAL_MINIO_SECRET_KEY', 'Token Not found'),
        secure=False)

    devMinioClient = Minio('10.2.32.24',
        access_key=os.getenv('DEV_MINIO_ACCESS_KEY', 'Token Not found'),
        secret_key=os.getenv('DEV_MINIO_SECRET_KEY', 'Token Not found'),
        secure=False)
    
    minioClient = devMinioClient

    try:
        minioClient.make_bucket(docker_bucket_name)
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        logger.info("Docker bucket already exists in minIO - %s" , docker_bucket_name)
    except ResponseError as err:
        raise

    try:
        minioClient.make_bucket(npm_bucket_name)
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        logger.info("NPM bucket already exists in minIO - %s" , npm_bucket_name)
    except ResponseError as err:
        raise

    # Build list of images to pull
    docker_images_to_download = []

    for docker_image in download_list:
        # Generate list of docker images
        if docker_image.tag:
            tags = docker_image.tag.split(',')
            for tag in tags:
                docker_image_to_download = docker_image.image + ':' + tag.strip()
                docker_images_to_download.append(docker_image_to_download)
        else:
            docker_images_to_download.append(docker_image_to_download)
        
        # Pull list of tags for this docker image and save to minio
        for docker_image_to_download in docker_images_to_download:

            dockerClient.images.pull(docker_image_to_download)
            docker_image = dockerClient.images.get(docker_image_to_download)
            docker_image_filename = 'xfer-' + docker_image_to_download.replace(':', '_') + '.tar'

            # Download docker image
            logger.info("writing docker_image to file - %s" , docker_image_filename)
            f = open(npm_path + 'npm.tar.gz', 'wb')
            for chunk in docker_image.save(chunk_size=2000000, named=True):
                f.write(chunk)
            file_size = os.fstat(f.fileno()).st_size
            f.close()

            # Upload docker image to minIO
            logger.info("upload to minIO - %s" , docker_image)
            try:
                file_data = open(npm_path + 'npm.tar.gz', 'rb')
                file_stat = os.stat(npm_path + 'npm.tar.gz')
                print(minioClient.put_object('docker', os.path.basename(npm_path + 'npm.tar.gz'), file_data, file_stat.st_size, metadata={"x-amz-test-key": "test-data"}))
                os.remove(npm_path + 'npm.tar.gz')
            except ResponseError as err:
                logger.info("upload docker to minIO failed - %s" , docker_image)
                print(err)