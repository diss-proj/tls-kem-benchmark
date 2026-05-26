import csv
from multiprocessing import Pool, freeze_support
import os
import subprocess
import networkmgmt
import sys

POOL_SIZE = 4

MEASUREMENTS_PER_TIMER = 20
TIMERS = 10

DEFAULT_SCENARIO_TO_TEST = 'scenario_packetloss.csv'
ALGORITHMS_TO_TEST = 'algorithms.csv'
MAIN_DIR = 'results'
ROW_NAMES = [0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

algorithmlist = []
algorithm_class_descriptions = []
scenariodescription = []

def run_subprocess(command, working_dir='.', expected_returncode=0):
    print(command)
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir
    )
    print(result.stdout)
    if(result.stderr):
        print(result.stderr)
    assert result.returncode == expected_returncode
    return result.stdout.decode('utf-8')

# do TLS handshake (s_timer.c)
def time_handshake(kex_alg, measurements):
    command = [
        'ip', 'netns', 'exec', 'cli_ns',
        './s_timer.o', kex_alg, str(measurements)
    ]
    result = run_subprocess(command)
    return [float(i) for i in result.strip().split(',')]

def run_timers(kex_alg, timer_pool):
    results_nested = timer_pool.starmap(time_handshake, [(kex_alg, MEASUREMENTS_PER_TIMER)] * TIMERS)
    return [item for sublist in results_nested for item in sublist]

# read algorithms.csv
def read_algorithms():
    if len(algorithmlist) > 0:
            return
    with open(ALGORITHMS_TO_TEST) as csv_file:
	    algor_classes = csv.reader(csv_file, delimiter=',')
	    for algor_class in algor_classes:
		    algorithms_of_certain_class = []
		    for algorithm in algor_class:
		            algorithms_of_certain_class.append(algorithm)
		    algorithm_class_descriptions.append(algorithms_of_certain_class.pop(0))
		    algorithmlist.append(algorithms_of_certain_class)
    return

# read handed scenario files
def read_testscenario(name_of_scenariofile):
    with open(name_of_scenariofile) as csv_file:
        network_scenario = csv.reader(csv_file, delimiter=',')
        for paramset in network_scenario:
            network_paramset = []
            for param in paramset:
                    network_paramset.append(param)
            paramsets.append(network_paramset)
        scenariodescription.append(paramsets[0][0])
        paramsets.pop(0)
    return

def make_dirs():
    if not os.path.exists(MAIN_DIR):
        os.makedirs(MAIN_DIR)
    directory = '{}/{}'.format(MAIN_DIR, scenariodescription[0])
    for algor_class in algorithm_class_descriptions:
        if not os.path.exists('{}/{}'.format(directory, algor_class)):
            os.makedirs('{}/{}'.format(directory, algor_class))
    return directory

def setup(name_of_scenariofile):
    read_algorithms()
    read_testscenario(name_of_scenariofile)
    return make_dirs()

# Main
if __name__ == '__main__':
    timer_pool = Pool(processes=POOL_SIZE)

    scenariofiles = []

# Check for handed scenarios
    if len(sys.argv) > 1:
        for i in range (1, len(sys.argv)):
            print(sys.argv[i])
            scenariofiles.append(sys.argv[i])
    else:
        scenariofiles.append(DEFAULT_SCENARIO_TO_TEST)

    for scenariofile in scenariofiles:
        paramsets = []
        directory = setup(scenariofile)

        # To get actual (emulated) RTT
        networkmgmt.change_qdisc('srv_ns', 'srv_ve', 0, paramsets[0][2], 0, 0, 0, 0, paramsets[0][7])
        networkmgmt.change_qdisc('cli_ns', 'cli_ve', 0, paramsets[0][9], 0, 0, 0, 0, paramsets[0][14])
        rtt_str = networkmgmt.get_rtt_ms()

            # set network parameters of scenario
        for paramset in paramsets:
            networkmgmt.change_qdisc('srv_ns', 'srv_ve', paramset[1], paramset[2], paramset[3], paramset[4], paramset[5], paramset[6], paramset[7])
            networkmgmt.change_qdisc('cli_ns', 'cli_ve', paramset[8], paramset[9], paramset[10], paramset[11], paramset[12], paramset[13], paramset[14])

            index = 0
            for algorithmclass in algorithmlist:
                for kex_alg in algorithmclass:
                    print('{}/{}/{}.csv'.format(directory, algorithm_class_descriptions[index], kex_alg))
                    with open('{}/{}/{}.csv'.format(directory, algorithm_class_descriptions[index], kex_alg),'a') as out:
                        csv_out = csv.writer(out)
                        result = run_timers(kex_alg, timer_pool)
                        result.insert(0, '{}'.format(ROW_NAMES[index]))
                        csv_out.writerow(result)
                index = index + 1
        scenariodescription.pop(0)

    timer_pool.close()
    timer_pool.join()
