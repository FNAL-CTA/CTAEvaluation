FROM almalinux/9-base

RUN dnf upgrade -y \
    && dnf clean all \
    && rm -rf /var/cache/dnf

RUN dnf -y install 'dnf-command(config-manager)'\
    && dnf clean all \
    && rm -rf /var/cache/dnf
RUN dnf config-manager --set-enabled crb

# Convenience stuff. Remove in production?
RUN dnf install -y git which nano wget jq sudo epel-release \
    && dnf clean all \
    && rm -rf /var/cache/dnf

ADD cta-public-5-alma9.repo  /etc/yum.repos.d/

RUN yum -y install cta-cli unzip \
    && yum clean all \
    && rm -rf /var/cache/yum

#fluentd install with tdagent
RUN yum install -y sudo
RUN curl -L https://toolbelt.treasuredata.com/sh/install-redhat-td-agent4.sh | sh


# From here we want to remake the container as this code will change
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN git clone https://github.com/ericvaandering/CTAEvaluation.git

#ADD tmp/eos-test-file-inject /root/eos-test-file-inject
#ADD tmp/eos-import-files-csv /root/eos-import-files-csv
#ADD tmp/libctacatalogue.so.0 /usr/lib64
#ADD tmp/libctacommon.so.0 /usr/lib64
#ADD tmp/libctardbms.so.0 /usr/lib64
#ADD tmp/libctardbmswrapper.so.0 /usr/lib64

#ADD cta-krb5.conf /etc/krb5.conf
#ADD cta-cli.conf /etc/cta/cta-cli.conf
#ADD cta-frontend-xrootd.conf /etc/cta/cta-frontend-xrootd.conf
#ADD eos.grpc.keytab /etc/cta/eos.grpc.keytab
#ADD ctafrontend_client_sss.keytab /etc/ctafrontend_client_sss.keytab
#RUN chmod o+rw /etc/ctafrontend_client_sss.keytab

RUN yum install jq -y

RUN td-agent-gem install fluent-plugin-parser-logfmt
RUN td-agent-gem install fluent-plugin-rename-key
RUN td-agent-gem install fluent-plugin-filter_typecast
#RUN td-agent-gem install fluent-plugin-multi-format-parser -v 1.0.0
ADD entrypoint.sh /

#RUN /usr/sbin/td-agent -c /etc/td-agent/td-agent.conf
ENTRYPOINT ["/entrypoint.sh"]
