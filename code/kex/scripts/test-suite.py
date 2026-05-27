###### TLS handshake duration test suite script

###### Imports
import csv
import os
from sys import argv, stdout
import pandas as pd
from networkmgmt import run_subprocess, change_network_settings
from definetests import headings
from tqdm import tqdm
from datetime import datetime, timezone
from multiprocessing import Pool

###### Globals
CLIENT_POOL_SIZE = 8
ALGORITHMS_CONFIG = './algorithms.csv' 
MEASUREMENTS_PER_TIMER = 5
RESULTS_DIR = './test-results/raw'
DEBUG=True

##### Setup
if __name__ == "__main__":
    saved_stdout = sys.stdout
    test_config_files = argv[1:]
    algorithms = {}
# algorithms is a dict of KEMs at different security levels.
# e.g. algorithms["secLevel1"] = ["hqc128", "mlkem512"]

    with open(ALGORITHMS_CONFIG, "r") as algs_file:
        for line in algs_file.readlines():
            _vals = line.split(",")
            algorithms[_vals[0]] = _vals[1:]

##### Results Directory Format Example
#   results
#       - packet_loss
#            - secLevel1
#                - hqc128
#                   - test_info.txt
#                   - batch-parameters.csv
#                   - batch-1.data
#                   -  batch-2.data

######################### Test Functions #####################################

##### time_handshake - from henrich et al 2023

def time_handshake(kem_algorithm: str):
    """time several tls 1.3 handshakes using a specific 
    KEM and record their durations.
    """
    command = [
        'ip', 'netns', 'exec', 'cli_ns',
        './s_timer.o', kem_algorithm, str(MEASUREMENTS_PER_TIMER), 
    ] 
    result = run_subprocess(command, debug=DEBUG)
    return [float(i) for i in result.strip().split(',')]

##### test_algorithm - run a full test set (e.g. packet loss) for one 
##### algorithm
def run_tests_with_pool(kem_algorithm: str, measurements: int):
    """times the handshakes for a batch using several threads
    Arguments:
    kem_algorithm - the OQS name (e.g. hqc128) of the algorithm being
        tested
    measurements - the total number of measurements needed
    """
    iterations = measurements // MEASUREMENTS_PER_TIMER
    commands = [(kem_algorithm,)] * iterations
    with Pool(CLIENT_POOL_SIZE) as pool:
        nested_results = pool.starmap(
            time_handshake, 
            commands
        )
    return [item for sublist in nested_results for item in sublist]

def test_algorithm(config_file: str, algorithm: str, results_dir: str):
    """Run all the test batches for one KEM e.g. hqc128
    as defined by a config file.

    Writes each batch's results to a .data file in the suplied results_dir.
    Also writes a batch-info.csv file and a README.txt file detailing the
    test time and platform.

    """
    with open(f"{results_dir}/README.txt", "w") as readme:
        timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d\t%H:%M:%S")
        readme.write(f"Batch Date and Time: {timestamp}\n")
        readme.write(f"Platform OS: {os.uname()[-2]}\n")
        readme.write(f"Platform Arch: {os.uname()[-1]}\n")


    with open(config_file, "r") as test_csv:
        total_samples = pd.read_csv(test_csv)['batch_count'].sum()
        # ^ get total size of the test set to display a progress bar
    
    pbar = tqdm(total=total_samples, desc=f"{config_file}: {algorithm}")
    with open(config_file, "r") as test_csv,\
    open(f"{results_dir}/batch-parameters.csv", "w") as batch_params_file:


        params_writer = csv.writer(batch_params_file)
        params_writer.writerow((['batch_number'] + headings))

        reader = csv.DictReader(test_csv)
        batch_number = 1

        for batch in reader:
            batch_size = int(batch["batch_count"])
            change_network_settings(
                packet_loss = batch["packet_loss"],
                delay = batch["delay"],
                client_rate = batch["client_rate"],
                server_rate = batch["server_rate"],
                init_cnwd_size = batch["init_cnwd_size"],
                mtu_bytes = batch["mtu_bytes"]
            )
            results = run_tests_with_pool(algorithm, batch_size)
            pbar.update(batch_size)
            with open(f"{results_dir}/batch-{batch_number}.data", "w") as batch_results:
                batch_results.write(str(results)[1:-1])
            params_writer.writerow(([batch_number] + list(batch.values())))
            batch_number += 1

    sys.stdout = saved_stdout
    pbar.close()

    

##### test_set - run a full test set (e.g. packet loss) for all algorithms
def test_set(config_file: str):
    """run a complete set of tests as defined by a config file,
    on every KEM defined in ALGORITHMS_CONFIG
    """
    test_set_name = config_file.split("/")[-1].removesuffix(".csv")
    results_path = f"{RESULTS_DIR}/{test_set_name}"
    os.makedirs(results_path, exist_ok=True)

    for security_level in algorithms.keys():
        sec_level_results_path = f"{results_path}/{security_level}"
        os.makedirs(sec_level_results_path, exist_ok=True)

        for algorithm in algorithms[security_level]:
            alg_results_path = f"{sec_level_results_path}/{algorithm}"
            os.makedirs(alg_results_path, exist_ok=True)
            test_algorithm(config_file, algorithm, alg_results_path)

######################### Testing ############################################
if __name__ == "__main__":
    for test_set_config in test_config_files:
        test_set(test_set_config)


