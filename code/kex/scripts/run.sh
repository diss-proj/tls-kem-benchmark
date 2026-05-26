#!/bin/bash
set -ex

sh scripts/setup.sh

export OPENSSL_CONF=/home/diss/mlkem-hqc-testing-framework/_build/oqs-provider/scripts/openssl-ca.cnf
export OPENSSL_MODULES=/home/diss/mlkem-hqc-testing-framework/_build/oqs-provider/_build/lib
rm -rf ./test-results/
python3 scripts/test-suite.py experiment-configs/latency.csv
#testscenarios/scenario_rate_cli.csv testscenarios/scenario_rate_both.csv testscenarios/scenario_rate_srv.csv testscenarios/scenario_rate_both_duplicate.csv

sh scripts/teardown.sh

python3 scripts/analyze.py results/delay_minRate 
#results/rate_both_duplicate 
#results/rate_srv results/rate_cli results/rate_both
