**Creating Docker Container for Account Service**
```bash
# This process for creating Flask Container needs improved
docker run -it -p 8080:8080 --name AccountService alpine
apk add --update python3 py3-pip
pip install flask

docker exec -it AccountService /bin/sh
```
