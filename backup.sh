#!/usr/bin/env bash
# (c) Martin Erzberger 2019, Chonghua Liu 2024
# Backup all certificates

set -euo pipefail

# Change into CA directory
DIR="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
cd $DIR

read -p "This will backup all certificates into a ZIP file. Are you sure? " -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  source ./variables.sh
  # Add Root CA
  zip certbackup.zip rootca/certs/* rootca/private/* -x *.open.pem
  # Add Issuing CA and certificates
  zip certbackup.zip issuingca/certs/* issuingca/private/* -x *.open.pem
  # Protect the backup file
  chmod 600 certbackup.zip
  exit 0
fi
echo "Aborted"
exit 1
