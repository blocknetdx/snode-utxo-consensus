import requests
import json
import time
from datetime import datetime

# Define the IP addresses to fetch the blockchain length from
ip_addresses = ['https://utils.blocknet.org/xrs/heights', 'http://fat-cake/xrs/heights']


while True:

    blockchain_lengths = {}
    for ip in ip_addresses:
        try:
            response = requests.get(ip, timeout=5)
            blockchain_length = response.json()
            blockchain_lengths[ip] = blockchain_length
        except requests.exceptions.RequestException as e:
            print(f"Failed to get data from {ip}. Error: {e}")
            blockchain_lengths[ip] = None

    # Print all the blockchain lengths
    for ip, lengths in blockchain_lengths.items():
        if lengths is not None:
            for key, value in lengths.items():
                print(f"{key}: {value} from {ip}")
        else:
            print(f"No data received from {ip}")

    # Check if all blockchain lengths match
    match = True
    reference = blockchain_lengths[ip_addresses[0]]
    faulty_nodes = []
    for ip in blockchain_lengths:
        if blockchain_lengths[ip] != reference:
            match = False
            faulty_nodes.append(ip)
    if match:
        print("All blockchain lengths match!")
    else:
        print("Blockchain lengths do not match.")
        print(f"Faulty nodes: {faulty_nodes}")
        # Resolve disputes by taking the majority of responses as the correct one
        resolved_data = {}
        for key, value in blockchain_lengths[ip_addresses[0]].items():
            values = [blockchain_lengths[ip][key] for ip in ip_addresses if blockchain_lengths[ip] is not None]
            resolved_data[key] = max(set(values), key=values.count)
        print(f"Resolved data: {resolved_data}")

    # Save data to log file
    data = {
        'timestamp': datetime.now().isoformat(),
        'faulty_nodes': faulty_nodes,
        'resolved_data': resolved_data,
        'servers': []
    }
    for ip, lengths in blockchain_lengths.items():
        if lengths is not None:
            server_data = {
                'ip': ip,
                'data': lengths
            }
            data['servers'].append(server_data)
        else:
            server_data = {
                'ip': ip,
                'data': 'No data received from this server'
            }
            data['servers'].append(server_data)

    with open('log.json', 'w') as log_file:
        json.dump(data, log_file)
    time.sleep(600)