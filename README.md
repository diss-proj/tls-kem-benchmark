# PQC TLS 1.3 Handshake Benchmarking framework

Based on Henrich et al 2023 [here](https://code.fbi.h-da.de/pqc-benchmarking/benchmarking-pqc-in-tls)

This framework executes a series of benchmarks to demonstrate the effect of varying network
characteristics on PQC TLS 1.3 handshake completion times. It's highly configurable, with
the build process and experiment parameters controlled by easy-to-understand scripts.

# Overview
This project creates two virtual network stacks, spawns an apache `httpd` web server on
the "server" stack and uses a python script to orchestrate threads which use the 
`o_timer` program to connect to the web server via virtual ethernet interfaces.

Between each set of tests, the python script uses the Linux `netem` network emulation
manager to change settings which simulate packet loss, transmission rates and 
packet latency on each stack's outgoing interface.

## Important Files
```
├── build.sh
├── httpd-conf/             - Apache HTTPD config files
│   ├── httpd.conf
│   └── httpd-ssl.conf
├── kex/
│   ├── algorithms.csv          - The algorithms to be tested
│   ├── experiment-configs/ - files which define each test set.
│   ├── __init__.py
│   ├── Makefile                - used to compile s_timer.c
│   ├── s_timer.c               - s_timer source code
│   ├── s_timer.o               - s_timer handshake timing program
│   ├── scripts/
│   │   ├── definetests.py      - creates the experiment config files in experiment-configs/
│   │   ├── __init__.py
│   │   ├── networkmgmt.py      - defines functions to alter virtual network settings
│   │   ├── run.sh              - runs setup.sh, test-suite.py, then teardown.sh
│   │   ├── setup.sh            - sets up virtual network and web server before testing
│   │   ├── teardown.sh
│   │   └── test-suite.py       - orchestrates the handshake tests
│   └── test-results/       - the raw results of each test set
├── openssl-conf/
│   └── openssl.cnf             - openssl config file
├── README.md                   - **you are here**
└── setup_ns.sh                 - defines emulated network
```

# Prerequisites
1. Ensure all dependencies are installed. `install-dependencies-ubuntu.sh` in this project's
home directory should ensure you have everything if you're on a similar distribution to 
Ubuntu 26.04 LTS.
2. **ENSURE /opt/ CAN BE SAFELY DELETED**. This project builds and installs several programs
to `/opt/`, deleting any exisitng files in the process. 

# Pre-Build Configuration
This project downloads, builds and installs OpenSSL, `oqs-provider`, `liboqs`, and 
Apache HTTPD. All 4 are largely configured at compile time, so to change their settings you
must modify this project's build files. The key settings to be aware of are:
## Liboqs configuraiton
`build.sh` configures the version of `liboqs` which is downloaded and built, and includes
compile-time flags which disable any per-platform optimization. You can enable optimised
algorithm implementations and enable additional non-standard PQC algorithms by changing
the `-D` cmake flags under `#build liboqs`. See [liboqs - CONFIGURE.md](https://github.com/open-quantum-safe/liboqs/blob/main/CONFIGURE.md#options-for-configuring-liboqs-builds)
## OpenSSL Configruation
This project uses OpenSSL v3.4.0 as defined by `OPENSSL_TAG` in `build.sh`. 
`./openssl-conf/openssl.cnf` contains general configuration settings like 
TLS 1.3 version and enabled KEM groups.
## HTTPD Configuration
By default HTTPD is configured in `worker` mode, which uses a pool of full system processes
to handle incoming requests rather a heirarchy of threaded processes. This paradigm is less
efficient but makes each connection independent of any other ongoing connections, which 
is essential to generate meaningful data with a paralellised test suite methodology.

`./httpd-conf/httpd.conf` defines how many processes are spawned. This should be altered
to ensure that each one gets its own core, a general guideline should be the system's total
logical CPU core count / 2.

### HTTPD Signature Algorithm
`build.sh` generates an ML-DSA-65 key (security level 3), which is used by default for
all test connections. This is defined by changing the `SIG_ALG` variable.

## Library location
By default, `build.sh` builds the test suite's libraries in `/opt/`, other programs assume
this is the case so it's recommended not to alter this behaviour. `build.sh` **WILL DELETE
ANYTHING IN /opt/, ENSURE THIS IS SAFE BEFORE PROCEEDING**

# Post-Build Configuration
## Defining Tests
You can define tests by defining CSV files in `./kex/scripts/definetests.py` and running it
from `./kex`. Each test's parameters follow the format of `change_network_settings()` in
`./kex/scripts/networkmgmt`, which documents how each should be formatted.

Update `run.sh` to pass your new test files to `test-suite.py`.
## Multi-Processing and CPU Affinity
This test suite's tests can be run in parallel by changing `CLIENT_POOL_SIZE` in 
`./kex/scripts/test-suite.py`. To ensure that client and server processes don't interfere
with each other, `run.sh` and `startup.sh` define CPU affinities for `httpd` and `test-suite.py`,
which ensure that their child processes run on seperate sets of cores.

By default client processes run on cores 0-7 and server processes cores 8-15. Ranges should be 
selected to ensure the following:
- There are no more client threads than assigned client CPU cores.
- There are no more server processes than assigned server CPU cores.
- client CPU threads + server CPU processes < total system CPU count (to ensure that other
system processes can use a spare core without interrupting a test process).

### Note - Bandwidth
**DO NOT ENABLE MULTIPLE TEST THREADS IN `test-suite.py` IF YOU'RE TEST INVOLVES BANDWIDTH
RESTRICTIONS**. The bandwidth of each interface is shared between that interface's processes/threads,
so multi-threaded testing with restricted bandwidth would cause processes to interfere with each other.

# Running the Tests
## Disabling Runtime Optimization
Runtime optimisation measures should be disabled before running any tests, see `README.md` in this
project's [wider benchmarking framework](https://github.com/diss-proj/mlkem-hqc-testing-framework)

## run.sh
Navigate to `./kex` and run the suite with `./scripts/run.sh`. If a previous test failed, you
might need to run `./scripts/teardown.sh` first.

## Results
Raw benchmark times will be stored in `./kex/test-results/` in the following format:
```
test-results/
└── raw/
    └── packet_loss/
        └── secLevel1/
            └── hqc128/
                ├── batch-1.data            - raw handshake time resultsfor a given batch
                ├── batch-2.data
                ...
                ├── batch-parameters.csv    - how each batch was configured
                └── README.txt              - metadata describing when and where the test
                                              was run.
```


