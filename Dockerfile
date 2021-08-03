FROM python:3
ENV PYTHONUNBUFFERED=1

MAINTAINER Taboola SRE

ADD . /opt/api_exporter
WORKDIR /opt/api_exporter
COPY requirements.txt ./
COPY start.sh /
RUN pip install --no-cache-dir -r requirements.txt
CMD ["/start.sh"]
EXPOSE 9115

