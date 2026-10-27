#!/bin/bash
set -euo pipefail

# This script is intended to run the Claude review process.
# Add the commands to execute the review below.

claude -p "Please review the code for correctness and style." \
       --output-format json \
       --max-turns 10
