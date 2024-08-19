#!/usr/bin/env bash
# (c) Martin Erzberger 2019, Chonghua Liu 2024

set -euo pipefail

# Change into CA directory
DIR="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
cd $DIR

cp variables.sh.example variables.sh
chmod +x variables.sh

mkdir -p rootca/private rootca/crl rootca/certs rootca/newcerts
mkdir -p issuingca/private issuingca/certs issuingca/csr issuingca/crl issuingca/newcerts
touch rootca/index.txt rootca/serial issuingca/index.txt issuingca/serial
echo 1000 > rootca/serial
echo 1000 > issuingca/serial
