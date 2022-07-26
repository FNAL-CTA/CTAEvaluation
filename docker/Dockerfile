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

RUN yum -y install centos-release-scl-rh centos-release-scl
RUN yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
RUN yum -y install postgresql14 postgresql14-libs
ENV PATH="/usr/pgsql-14/bin:${PATH}"

RUN yum install -y rh-python38 rh-python38-python-devel oracle-instantclient19.3-basic \
                   eos-client protobuf3 grpc-devel xrootd-client xrootd-client-libs libarchive libarchive-devel \
                   mt-st mtx lsscsi \
    && yum clean all \
    && rm -rf /var/cache/yum

# Why we have a version mis-match I don't know
RUN ln -s /opt/eos/xrootd/lib64/libXrdCl.so.2 /usr/lib64/libXrdCl.so.2

RUN scl enable rh-python38 bash
RUN scl enable rh-python38 bash
RUN /opt/rh/rh-python38/root/usr/bin/pip3 install --upgrade protobuf sqlalchemy psycopg2-binary python-libarchive
#RUN /opt/rh/rh-python38/root/usr/bin/pip3 install --upgrade protobuf sqlalchemy psycopg2 python-libarchive


#RUN pip3 install --upgrade protobuf sqlalchemy psycopg2 python-libarchive

# From here we want to remake the container as this code will change
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache

RUN git clone https://github.com/ericvaandering/CTAEvaluation.git

ADD tmp/eos-test-file-inject /root/eos-test-file-inject
ADD tmp/eos-import-files-csv /root/eos-import-files-csv
