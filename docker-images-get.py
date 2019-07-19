import docker

client = docker.from_env()

client.images.pull('nginx')