#!/bin/bash

set -euxo pipefail

PACKAGE_NAME="${1:-}"

if [ -z $PACKAGE_NAME ]; then
    echo "Usage: $0 <package name>"
    exit 1
fi


echo "Installing dependencies for $PACKAGE_NAME"

# create and activate virtualenv - some containers
# already have a virtualenv installed, so we just
# activate.
if [ ! -e ~/venv/bin/activate ]; then
    python -m venv ~/venv
fi
source ~/venv/bin/activate

cd "$PACKAGE_NAME"

pip install -r requirements/development.txt

echo "Running tests for $PACKAGE_NAME"

pytest -vv tests/

#if [ -f manage.py ]; then
#  python manage.py circleci-test
#else
#  pytest --cov=${PYTHON_COVERAGE_PACKAGE} --cov-report=html:test-reports/htmlcov --junit-xml=test-reports/pytest
#fi

