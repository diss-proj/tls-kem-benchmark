# Script to create the CSV files which define each test set.

# imports
import csv
import os


# globals
headings = [
    'batch_count',
    'packet_loss',
    'delay',
    'client_rate',
    'server_rate',
    'init_cnwd_size',
    'mtu_bytes'
]

CONFIG_DIR = './experiment-configs'


# setup
if os.getcwd().strip("/").endswith('/scripts'):
    print("experiment scripts can't be run from within ./scripts")
    exit(1)


# functions
def write_csv_rule(
    writer: csv.writer,
    batch_count: int = 500,
    packet_loss: int = 0,
    delay: int = 1,
    client_rate: int = 1000000,
    server_rate: int = 1000000,
    init_cwnd_size: int = 10,
    mtu_bytes: int = 1500
    ):
    writer.writerow([
        f'{batch_count}',
        f'{packet_loss}',
        f'{delay}',
        f'{client_rate}',
        f'{server_rate}',
        f'{init_cwnd_size}',
        f'{mtu_bytes}',
    ])

# Create the CSVs
os.makedirs(CONFIG_DIR, exist_ok=True)

## Packet loss
with open(f'{CONFIG_DIR}/packet_loss.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for rate in range(0,6,1):
        write_csv_rule(writer, packet_loss=rate)
    for rate in range(6,11,1):
        write_csv_rule(writer, packet_loss=rate, batch_count=250)
    for rate in range(11,21,1):
        write_csv_rule(writer, packet_loss=rate, batch_count=200)
    #for rate in range(25,61, 5):
    #    write_csv_rule(writer, packet_loss=rate, batch_count=100)

## Latency/Delay
with open(f'{CONFIG_DIR}/latency.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for duration in range(1,16,1):
        write_csv_rule(writer, delay=duration)
    for duration in range(20,51,5):
        write_csv_rule(writer, delay=duration)
    for duration in range(75,151,25):
        write_csv_rule(writer, delay=duration)


## Bandwidth 
# client -> server
with open(f'{CONFIG_DIR}/bandwidth-client-to-server.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for rate in range(2,10,2):
        write_csv_rule(writer, client_rate=f'0.0{rate}', batch_count=200)
    write_csv_rule(writer, client_rate=f'0.1', batch_count=200)
    for rate in range(2,10,2):
        write_csv_rule(writer, client_rate=f'0.{rate}', batch_count=200)
    for rate in range(1,11,1):
        write_csv_rule(writer, client_rate=rate)
    for rate in range(15,51,5):
        write_csv_rule(writer, client_rate=rate)
    for rate in range(75,201,25):
        write_csv_rule(writer, client_rate=rate)
# server -> client
with open(f'{CONFIG_DIR}/bandwidth-server-to-client.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for rate in range(2,10,2):
        write_csv_rule(writer, server_rate=f'0.0{rate}', batch_count=200)
    write_csv_rule(writer, server_rate=f'0.1', batch_count=200)
    for rate in range(2,10,2):
        write_csv_rule(writer, server_rate=f'0.{rate}', batch_count=200)
    for rate in range(1,11,1):
        write_csv_rule(writer, server_rate=rate)
    for rate in range(15,51,5):
        write_csv_rule(writer, server_rate=rate)
    for rate in range(75,201,25):
        write_csv_rule(writer, server_rate=rate)
# bidirectional
with open(f'{CONFIG_DIR}/bandwidth-bidirectional.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for rate in range(2,10,2):
        write_csv_rule(writer, server_rate=f'0.0{rate}', client_rate=f'0.0{rate}', batch_count=200)
    write_csv_rule(writer, server_rate=f'0.1', client_rate=f'0.1', batch_count=200)
    for rate in range(2,10,2):
        write_csv_rule(writer, server_rate=f'0.{rate}', client_rate=f'0.{rate}', batch_count=200)
    for rate in range(1,11,1):
        write_csv_rule(writer, server_rate=rate, client_rate=rate)
    for rate in range(15,51,5):
        write_csv_rule(writer, server_rate=rate, client_rate=rate)
    for rate in range(75,201,25): 
        write_csv_rule(writer, server_rate=rate, client_rate=rate)

## TCP ICW Size
# ideal
with open(f'{CONFIG_DIR}/icw-size-ideal.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for packets in range(1,21,1):
        write_csv_rule(writer, init_cwnd_size=packets, batch_count=200)

# packet loss 5%
with open(f'{CONFIG_DIR}/icw-size-5%-packet-loss.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for packets in range(1,21,1):
        write_csv_rule(writer, packet_loss=5, init_cwnd_size=packets, batch_count=200)

# packet loss 20%
with open(f'{CONFIG_DIR}/icw-size-20%-packet-loss.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for packets in range(1,21,1):
        write_csv_rule(writer, packet_loss=20, init_cwnd_size=packets, batch_count=200)

# latency 15ms
with open(f'{CONFIG_DIR}/icw-size-15ms-latency.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for packets in range(1,21,1):
        write_csv_rule(writer, delay=15, init_cwnd_size=packets, batch_count=200)

# latency 100ms
with open(f'{CONFIG_DIR}/icw-size-100ms-latency.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for packets in range(1,21,1):
        write_csv_rule(writer, delay=100, init_cwnd_size=packets, batch_count=200)

# bandwidth 0.1MBit/s
with open(f'{CONFIG_DIR}/icw-size-100kbit-bandwidth.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for packets in range(1,21,1):
        write_csv_rule(writer, client_rate=0.1, server_rate=0.1,
        init_cwnd_size=packets, batch_count=200)

# bandwidth 5MBit/s
with open(f'{CONFIG_DIR}/icw-size-5mbit-bandwidth.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for packets in range(1,21,1):
        write_csv_rule(writer, client_rate=5, server_rate=5,
        init_cwnd_size=packets, batch_count=200)

## MTU Size
# ideal
with open(f'{CONFIG_DIR}/mtu-size-ideal.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for bytes in range(1500,9001,1500):
        write_csv_rule(writer, mtu_bytes=bytes, batch_count=200)

# packet loss 5%
with open(f'{CONFIG_DIR}/mtu-size-5%-packet-loss.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for bytes in range(1500,9001,1500):
        write_csv_rule(writer, packet_loss=5, mtu_bytes=bytes, batch_count=200)

# packet loss 20%
with open(f'{CONFIG_DIR}/mtu-size-20%-packet-loss.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for bytes in range(1500,9001,1500):
        write_csv_rule(writer, packet_loss=20, mtu_bytes=bytes, batch_count=200)

# latency 15ms
with open(f'{CONFIG_DIR}/mtu-size-15ms-latency.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for bytes in range(1500,9001,1500):
        write_csv_rule(writer, delay=15, mtu_bytes=bytes, batch_count=200)

# latency 100ms
with open(f'{CONFIG_DIR}/mtu-size-100ms-latency.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for bytes in range(1500,9001,1500):
        write_csv_rule(writer, delay=100, mtu_bytes=bytes, batch_count=200)

# bandwidth 0.1MBit/s
with open(f'{CONFIG_DIR}/mtu-size-100kbit-bandwidth.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for bytes in range(1500,9001,1500):
        write_csv_rule(writer, client_rate=0.1, server_rate=0.1,
        mtu_bytes=bytes, batch_count=200)

# bandwidth 5MBit/s
with open(f'{CONFIG_DIR}/mtu-size-5mbit-bandwidth.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(headings)
    for bytes in range(1500,9001,1500):
        write_csv_rule(writer, client_rate=5, server_rate=5,
        mtu_bytes=bytes, batch_count=200)
