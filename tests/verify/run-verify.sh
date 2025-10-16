#!/bin/bash
# ------------------------------------------------------------------------------
# Run all SPARQL verification tests in /test/verify/
# Logs results to a timestamped file under ./logs/
#
# Usage: ./run-verify.sh <endpointURL>
# Example: ./run-verify.sh http://localhost:7200/repositories/data-product
#
# Requirements:
#   - Bash shell
#   - SPARQL endpoint accepting POST queries
#   - curl installed
# ------------------------------------------------------------------------------

ENDPOINT="$1"

if [ -z "$ENDPOINT" ]; then
  echo "Usage: $0 <SPARQL_endpoint_URL>"
  echo "Example: $0 http://localhost:7200/repositories/data-product"
  exit 1
fi

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOGDIR="./logs"
LOGFILE="$LOGDIR/verify-${TIMESTAMP}.log"

mkdir -p "$LOGDIR"

echo "Running ontology verification suite against: $ENDPOINT"
echo "Results will be logged to: $LOGFILE"
echo "------------------------------------------------------" | tee -a "$LOGFILE"

for FILE in $(ls -1 *.sparql | sort); do
  echo "▶ Running $FILE" | tee -a "$LOGFILE"
  echo "------------------------------------------------------" | tee -a "$LOGFILE"

  RESULT=$(curl -s -X POST \
       -H "Content-Type: application/sparql-query" \
       --data-binary "@$FILE" \
       "$ENDPOINT")

  echo "$RESULT" | tee -a "$LOGFILE"
  
  if echo "$RESULT" | grep -qE "http|IRI"; then
    echo "⚠️  Issues detected in $FILE" | tee -a "$LOGFILE"
  else
    echo "✅  Passed" | tee -a "$LOGFILE"
  fi

  echo "" | tee -a "$LOGFILE"
done

echo "------------------------------------------------------" | tee -a "$LOGFILE"
echo "Verification complete. Full results saved in $LOGFILE"
