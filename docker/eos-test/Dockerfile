FROM almalinux:9.3


#RUN dnf install -y 'dnf-command(config-manager)'
#RUN dnf config-manager --set-enabled crb
RUN dnf install -y epel-release.noarch
RUN dnf upgrade -y && \
    dnf install -y \
#        python-pip \
        git which nano wget gcc \
        && \
    dnf clean all && \
    rm -rf /var/cache/dnf

ADD eos-xrootd-el9.repo /etc/yum.repos.d/eos-xrootd.repo
#ADD oracle-instant-client-el9.repo /etc/yum.repos.d

#RUN wget https://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol9 -O /etc/pki/rpm-gpg/RPM-GPG-KEY-oracle

#RUN dnf -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
#RUN dnf -y install postgresql14 postgresql14-libs
#ENV PATH="/usr/pgsql-14/bin:${PATH}"

#RUN dnf -y install  https://download.oracle.com/otn_software/linux/instantclient/1912000/oracle-instantclient19.12-basiclite-19.12.0.0.0-1.x86_64.rpm

# Removed libarchive-devel
RUN dnf install -y eos-client eos-test protobuf grpc-devel xrootd-client xrootd-client-libs libarchive \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Why we have a version mis-match I don't know
#RUN ln -s /opt/eos/xrootd/lib64/libXrdCl.so.2 /usr/lib64/libXrdCl.so.2

# Good through here

#RUN pip install --upgrade protobuf sqlalchemy psycopg2-binary python-libarchive
#RUN /opt/rh/rh-python38/root/usr/bin/pip3 install --upgrade protobuf sqlalchemy psycopg2 python-libarchive


#RUN pip3 install --upgrade protobuf sqlalchemy psycopg2 python-libarchive

# Install CEPH stuff
#RUN rpm --import 'https://download.ceph.com/keys/release.asc'
# libradosstriper1
RUN dnf -y install librados2

# Breaks here. No surprise CTA RPMs for EL7 don't install. Wait for EL9 RPMs

#ADD tmp/cta-cli-4-4958535git71bda8fb.el7.cern.x86_64.rpm /root/cta-cli-4-4958535git71bda8fb.el7.cern.x86_64.rpm
#ADD tmp/cta-lib-common-4-4958535git71bda8fb.el7.cern.x86_64.rpm /root/cta-common-4-4958535git71bda8fb.el7.cern.x86_64.rpm

#RUN yum -y install /root/*.rpm

# From here we want to remake the container as this code will change
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git clone https://github.com/ericvaandering/CTAEvaluation.git

#ADD cta-krb5.conf /etc/krb5.conf
#ADD cta-cli.conf /etc/cta/cta-cli.conf
#ADD cta-frontend-xrootd.conf /etc/cta/cta-frontend-xrootd.conf
#ADD eos.grpc.keytab /etc/cta/eos.grpc.keytab

ADD entrypoint.sh /
