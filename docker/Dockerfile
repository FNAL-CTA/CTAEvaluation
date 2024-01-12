FROM gitlab-registry.cern.ch/linuxsupport/cc7-base

RUN yum upgrade -y \
    && yum clean all \
    && rm -rf /var/cache/yum

# Reevaluate how much of this we need

RUN yum install -y git curl which nano wget gcc \
    && yum clean all \
    && rm -rf /var/cache/yum

ADD cta-public-5.repo /etc/yum.repos.d/

RUN yum install -y cta-release cta-cli
RUN cta-versionlock config eos5
RUN cta-versionlock apply 


#ADD eos-xrootd.repo /etc/yum.repos.d/
RUN yum-config-manager --add-repo "https://storage-ci.web.cern.ch/storage-ci/eos/diopside/tag/testing/el-7/x86_64/" \
 && yum-config-manager --add-repo "https://storage-ci.web.cern.ch/storage-ci/eos/diopside-depend/el-7/x86_64/"

ADD oracle-instant-client.repo /etc/yum.repos.d

RUN wget https://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol7 -O /etc/pki/rpm-gpg/RPM-GPG-KEY-oracle

RUN yum -y install centos-release-scl-rh centos-release-scl
RUN yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
RUN yum -y install postgresql14 postgresql14-libs
ENV PATH="/usr/pgsql-14/bin:${PATH}"

# Some things are not signed
RUN yum install -y --nogpgcheck eos-client # grpc-devel

# Some are
RUN yum install -y rh-python38 rh-python38-python-devel oracle-instantclient19.3-basic \
                   protobuf3  xrootd-client xrootd-client-libs libarchive libarchive-devel \
                   mt-st mtx lsscsi \
    && yum clean all \
    && rm -rf /var/cache/yum

# Why we have a version mis-match I don't know
RUN ln -s /opt/eos/xrootd/lib64/libXrdCl.so.2 /usr/lib64/libXrdCl.so.2

RUN /opt/rh/rh-python38/root/usr/bin/pip3 install --upgrade protobuf sqlalchemy psycopg2-binary python-libarchive

# Install CEPH stuff
RUN rpm --import 'https://download.ceph.com/keys/release.asc'
RUN yum -y install http://download.ceph.com/rpm-15.2.15/el7/x86_64/librados2-15.2.15-0.el7.x86_64.rpm \
 http://download.ceph.com/rpm-15.2.15/el7/x86_64/libradosstriper1-15.2.15-0.el7.x86_64.rpm

#RUN yum -y --skip-broken  --nogpgcheck install cta-cli-5.10.0-2.el7.cern.x86_64
ADD python38.sh /etc/profile.d/

## From here we want to remake the container as this code will change
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git clone https://github.com/ericvaandering/CTAEvaluation.git

#ADD cta-krb5.conf /etc/krb5.conf
#ADD cta-cli.conf /etc/cta/cta-cli.conf
#ADD cta-frontend-xrootd.conf /etc/cta/cta-frontend-xrootd.conf
#ADD eos.grpc.keytab /etc/cta/eos.grpc.keytab

ADD entrypoint.sh /
