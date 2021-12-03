#!/bin/bash

# @project        The CERN Tape Archive (CTA)
# @copyright      Copyright(C) 2021 CERN
# @license        This program is free software: you can redistribute it and/or modify
#                 it under the terms of the GNU General Public License as published by
#                 the Free Software Foundation, either version 3 of the License, or
#                 (at your option) any later version.
#
#                 This program is distributed in the hope that it will be useful,
#                 but WITHOUT ANY WARRANTY; without even the implied warranty of
#                 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#                 GNU General Public License for more details.
#
#                 You should have received a copy of the GNU General Public License
#                 along with this program.  If not, see <http://www.gnu.org/licenses/>.

EOSINSTANCE=ctaeos
TEST_FILE_NAME=3M-test

# get some common useful helpers for krb5
. /root/client_helper.sh

eospower_kdestroy
eospower_kinit

echo "xrdcp /bin/dwp root://${EOSINSTANCE}//eos/ctaeos/cta/${TEST_FILE_NAME}"
xrdcp /bin/dwp root://${EOSINSTANCE}//eos/ctaeos/cta/${TEST_FILE_NAME}

SECONDS_PASSED=0
WAIT_FOR_ARCHIVED_FILE_TIMEOUT=90
while test 0 = `eos root://${EOSINSTANCE} info /eos/ctaeos/cta/${TEST_FILE_NAME} | awk '{print $4;}' | grep tape | wc -l`; do
  echo "Waiting for file to be archived to tape: Seconds passed = ${SECONDS_PASSED}"
  sleep 1
  let SECONDS_PASSED=SECONDS_PASSED+1

  if test ${SECONDS_PASSED} == ${WAIT_FOR_ARCHIVED_FILE_TIMEOUT}; then
    echo "Timed out after ${WAIT_FOR_ARCHIVED_FILE_TIMEOUT} seconds waiting for file to be archived to tape"
    exit 1
  fi
done

echo
echo "FILE ARCHIVED TO TAPE"
echo
eos root://${EOSINSTANCE} info /eos/ctaeos/cta/${TEST_FILE_NAME}
echo
echo "Information about the testing file:"
echo "********"
  eos root://${EOSINSTANCE} attr ls /eos/ctaeos/cta/${TEST_FILE_NAME}
  eos root://${EOSINSTANCE} ls -l /eos/ctaeos/cta/${TEST_FILE_NAME}
  eos root://${EOSINSTANCE} info /eos/ctaeos/cta/${TEST_FILE_NAME}
echo
echo "Removing disk replica as poweruser1:powerusers (12001:1200)"
# XrdSecPROTOCOL=sss eos -r 12001 1200 root://${EOSINSTANCE} file drop /eos/ctaeos/cta/${TEST_FILE_NAME} 1
XrdSecPROTOCOL=sss eos -r 0 0 root://${EOSINSTANCE} file drop /eos/ctaeos/cta/${TEST_FILE_NAME} 1
echo
echo "Information about the testing file without disk replica"
  eos root://${EOSINSTANCE} ls -l /eos/ctaeos/cta/${TEST_FILE_NAME}
  eos root://${EOSINSTANCE} info /eos/ctaeos/cta/${TEST_FILE_NAME}
echo
echo "Trigerring EOS retrieve workflow as poweruser1:powerusers (12001:1200)"
#echo "XrdSecPROTOCOL=sss xrdfs ${EOSINSTANCE} prepare -s \"/eos/ctaeos/cta/${TEST_FILE_NAME}?eos.ruid=12001&eos.rgid=1200\""
#  XrdSecPROTOCOL=sss xrdfs ${EOSINSTANCE} prepare -s "/eos/ctaeos/cta/${TEST_FILE_NAME}?eos.ruid=12001&eos.rgid=1200"

# We need the -s as we are staging the files from tape (see xrootd prepare definition)
KRB5CCNAME=/tmp/${EOSPOWER_USER}/krb5cc_0 XrdSecPROTOCOL=krb5 xrdfs ${EOSINSTANCE} prepare -s /eos/ctaeos/cta/${TEST_FILE_NAME}

# Wait for the copy to appear on disk
SECONDS_PASSED=0
WAIT_FOR_RETRIEVED_FILE_TIMEOUT=90
while test 0 = `eos root://${EOSINSTANCE} info /eos/ctaeos/cta/${TEST_FILE_NAME} | awk '{print $4;}' | grep -F "default.0" | wc -l`; do
  echo "Waiting for file to be retrieved from tape: Seconds passed = ${SECONDS_PASSED}"
  sleep 1
  let SECONDS_PASSED=SECONDS_PASSED+1

  if test ${SECONDS_PASSED} == ${WAIT_FOR_RETRIEVED_FILE_TIMEOUT}; then
    echo "Timed out after ${WAIT_FOR_RETRIEVED_FILE_TIMEOUT} seconds waiting for file to be retrieved from tape"
    exit 1
  fi
done
echo
echo "FILE RETRIEVED FROM DISK"
echo
echo "Information about the testing file:"
echo "********"
  eos root://${EOSINSTANCE} attr ls /eos/ctaeos/cta/${TEST_FILE_NAME}
  eos root://${EOSINSTANCE} ls -l /eos/ctaeos/cta/${TEST_FILE_NAME}
  eos root://${EOSINSTANCE} info /eos/ctaeos/cta/${TEST_FILE_NAME}


xrdcp root://${EOSINSTANCE}//eos/ctaeos/cta/${TEST_FILE_NAME} /root/test.group

# Delete the file so it doesn't interfere with tests in client_ar.sh
echo "eos root://${EOSINSTANCE} rm /eos/ctaeos/cta/${TEST_FILE_NAME}"
eos root://${EOSINSTANCE} rm /eos/ctaeos/cta/${TEST_FILE_NAME}

exit
