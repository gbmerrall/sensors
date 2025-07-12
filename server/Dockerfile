# if you're building this cross-platform see this guide 
# https://docs.docker.com/build/building/multi-platform/
# I used the QEMU option

# docker buildx build --platform linux/arm64,linux/amd64 -t sensors:latest .

# external will be mounted as a volume

# example run
# docker run --rm -p 5000:5000 --mount source=sensorsVolume,destination=external sensors

FROM python:3.12-slim-bookworm

# we need git to install any git based dependencies in requirements.txt
RUN apt-get update && apt-get install -y git

WORKDIR /sensors
COPY requirements.txt requirements.txt
RUN pip install --no-cache -r requirements.txt

COPY app app
COPY external/sensors.json external/sensors.json
COPY run.sh ./
RUN chmod a+x run.sh

EXPOSE 5000
ENTRYPOINT ["./run.sh"]