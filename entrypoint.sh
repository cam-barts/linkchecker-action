#!/bin/sh
set -e

cd $GITHUB_WORKSPACE

set +e
# OUTPUT=$(python /check-links.py)
python /check-links.py
SUCCESS=$EXIT_CODE
# echo "$OUTPUT"
set -e

exit $SUCCESS