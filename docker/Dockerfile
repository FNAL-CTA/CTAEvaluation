FROM gitlab-registry.cern.ch/linuxsupport/cc7-base

RUN yum upgrade -y \
    && yum clean all \
    && rm -rf /var/cache/yum

RUN yum install -y gcc \
    && yum clean all \
    && rm -rf /var/cache/yum

RUN yum install -y git curl which nano python3 python3-devel postgresql libpqxx-devel \
    && yum clean all \
    && rm -rf /var/cache/yum
RUN pip3 install --upgrade protobuf sqlalchemy psycopg2

RUN git clone https://github.com/ericvaandering/CTAEvaluation.git


