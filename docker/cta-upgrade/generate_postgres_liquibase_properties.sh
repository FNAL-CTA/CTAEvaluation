#!/bin/bash

# This file comes from the "automatic" CTA upgrade container

# postgresql:postgresql://username:password@hostname/database

set -e # exit on first failure

# Ignore comments from catalogue conf and remove preceding "oracle:" string
CATALOGUE_CONF=`cat /shared/etc_cta/cta-catalogue.conf | grep -v '^#' | sed -e "s/^postgresql:postgresql:\/\///"`

CATALOGUE_HOST=${CATALOGUE_CONF#*@}

CATALOGUE_CONF_PREFIX=${CATALOGUE_CONF%@*}
CATALOGUE_USERNAME=$(echo ${CATALOGUE_CONF_PREFIX%:*} | sed 's/ //g')
CATALOGUE_PASSWORD=${CATALOGUE_CONF_PREFIX#*:}

echo "#
url: jdbc:postgresql://${CATALOGUE_HOST}
username: ${CATALOGUE_USERNAME}
password: ${CATALOGUE_PASSWORD}
driver: org.postgresql.Driver
classpath: /usr/share/java/postgresql-jdbc.jar
liquibase.headless: true"
