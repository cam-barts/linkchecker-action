#!/bin/sh
set -e

cd $GITHUB_WORKSPACE

set +e
OUTPUT=$(python /check-links.py)
SUCCESS=$?
echo $OUTPUT
set -e

exit $SUCCESS