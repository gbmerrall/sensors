# Dockerfile for dashboard service
# if you're building this cross-platform see this guide 
# https://docs.docker.com/build/building/multi-platform/
# I used the QEMU option

# docker buildx build --platform linux/arm64,linux/amd64 -t gmerrall/sensors_dashbaoard:latest .

# dashboard/external will be mounted as a volume

# example run
# docker run --rm -p 5050:5050 --mount source=sensorsVolume,destination=/dashboard/external sensors_dashboard

FROM python:3.12-slim-bookworm

WORKDIR /dashboard
COPY requirements.txt requirements.txt
RUN pip install --no-cache -r requirements.txt

COPY main.py ./
COPY src src
COPY run.sh ./
RUN chmod a+x run.sh

EXPOSE 5050
ENTRYPOINT ["./run.sh"] 