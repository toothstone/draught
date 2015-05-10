FROM python:2.7
MAINTAINER Peter Klausing <peter_klausing@wh2.tu-dresden.de>


ENV DEBIAN_FRONTEND=noninteractive \
	LC_ALL=C

RUN apt-get update && apt-get install -y --no-install-recommends \
	libldap2-dev \
	libsasl2-dev \
	libmysqlclient-dev \
	libxml2-dev \
	libxslt1-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


RUN pip install uwsgi

RUN addgroup --gid 9999 draught && \
	adduser --uid 9999 --gid 9999 --disabled-password --gecos "Application" draught

RUN mkdir /var/log/draught && \
    chown draught:draught /var/log/draught

ADD . /home/draught/draught

WORKDIR /home/draught/draught
RUN chown -R draught:draught /home/draught/draught

RUN pip install -r requirements.txt


EXPOSE 5000

USER draught
CMD ["/home/draught/draught/start.sh"]
