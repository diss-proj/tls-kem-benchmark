#!/bin/bash
TEST_CPUS="0-7"
# which CPUs should be used for testing processes
# shouldn't be the same as the ones hosting the test web servers.
set -ex

sh scripts/teardown.sh
sh scripts/setup.sh
python3 scripts/definetests.py

export OPENSSL_CONF=/opt/openssl/ssl/openssl.cnf
export OPENSSL_MODULES=/opt/openssl/lib/ossl-modules
taskset -c ${TEST_CPUS} python3 scripts/test-suite.py experiment-configs/latency.csv
#testscenarios/scenario_rate_cli.csv testscenarios/scenario_rate_both.csv testscenarios/scenario_rate_srv.csv testscenarios/scenario_rate_both_duplicate.csv

sh scripts/teardown.sh

#python3 scripts/analyze.py results/delay_minRate 
#results/rate_both_duplicate 
#results/rate_srv results/rate_cli results/rate_both
