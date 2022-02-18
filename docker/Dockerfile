FROM gitlab-registry.cern.ch/linuxsupport/cc7-base

RUN yum upgrade -y \
    && yum clean all \
    && rm -rf /var/cache/yum

RUN yum install -y git curl which nano wget \
    && yum clean all \
    && rm -rf /var/cache/yum

ADD eos-xrootd.repo /etc/yum.repos.d/eos-xrootd.repo
ADD oracle-instant-client.repo /etc/yum.repos.d

RUN wget https://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol7 -O /etc/pki/rpm-gpg/RPM-GPG-KEY-oracle

RUN yum install -y gcc \
    && yum clean all \
    && rm -rf /var/cache/yum

RUN yum install -y python3 python3-devel postgresql libpqxx-devel oracle-instantclient19.3-basic \
                   eos-client protobuf3 grpc-devel xrootd-client-libs \
    && yum clean all \
    && rm -rf /var/cache/yum

# Why we have a version mis-match I don't know
RUN ln -s /opt/eos/xrootd/lib64/libXrdCl.so.2 /usr/lib64/libXrdCl.so.2

RUN pip3 install --upgrade protobuf sqlalchemy psycopg2

# From here we want to remake the container as this code will change
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache

RUN git clone https://github.com/ericvaandering/CTAEvaluation.git

ADD tmp/eos-test-file-inject /root/eos-test-file-inject
ADD tmp/eos-import-files-csv /root/eos-import-files-csv
