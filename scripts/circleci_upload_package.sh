#!/bin/bash

set -euxo pipefail

PACKAGE_NAME="${1:-}"

if [ -z $PACKAGE_NAME ]; then
    echo "Usage: $0 <package name>"
    exit 1
fi

# do relative to the script
BASEDIR=`dirname $0`
PACKAGEDIR="$BASEDIR/../$PACKAGE_NAME"

cd "$PACKAGEDIR"

rm -rf dist build trade_common.egg-info
export TWINE_USERNAME="$LAD_PYPI_USER"
export TWINE_PASSWORD="$LAD_PYPI_PASS"

python setup.py sdist bdist_wheel

twine upload dist/*