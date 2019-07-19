# airgap-content-pipeline
A bunch of code to transport internet content and resources to an offline environment 

# Components
- Content manager to manage content metadata for download and scheduling
- Downloader
- Unpacking scripts for airgapped environment

# Content
- None

# In progress
- Docker Containers
- Helm Charts
- Git repositories
- File URLs

# Prereqs

Start a redis instance
```
docker run -d -p 6379:6379 --name airgapcms-redis redis
```

Start a minio instance
```
docker run -d -p 9000:9000 --name airgapcms-minio \
-e "MINIO_ACCESS_KEY=AIRGAPCMS12345" \
-e "MINIO_SECRET_KEY=AIRGAPCMS12345AIRGAPCMS12345AIRGAPCMS12345" \
-v /mnt/minio/data:/data \
-v /mnt/minio/config:/root/.minio \
minio/minio server /data
```