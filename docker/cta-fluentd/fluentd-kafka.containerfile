ARG VERSION=v1.16.2-debian-1.1
FROM fluentd:${VERSION}

USER root
RUN apt update -y
RUN apt install -y ruby-dev
RUN gem install ruby-kafka
RUN gem install fluent-plugin-kafka
RUN gem install fluent-plugin-filter_typecast
