import requests
import json
import time
from datetime import datetime
from collections import Counter
from threading import Thread

# Define the IP addresses to fetch the blockchain length from
ip_addresses = ['http://130.185.119.91/', 'https://utils.blocknet.org/', 'http://api.blockinbrick.com/']


# 'http://75.119.157.65/'


def fake_data():
    global ip_addresses
    my_dict = {
        'url_node1': {
            'BLOCK': (2874546, 'aaa'),
            'DASH': (1813785, '000000000000002dadab73fb1880a606a6105156eed3451619abf820c5e34a0e'),
            'LTC': (2413782, 'd89ee7a66506f97ceca7a40b2b853ac2d7260f78cff754467219d252e89b5a65'),
            'PIVX': (3726151, '6e248221277662fd0fc4758ef14dc5c86b30d5cf0687a6b544a76f20e279470a'),
            'SYS': (1556147, '481eca73fe77bd5c93a795f39d9ee6161bf7fd90d854649a992527070b5ca9e1')},
        'url_node2': {
            'BLOCK': (2874546, 'bbb'),
            'DASH': (1813785, '000000000000002dadab73fb1880a606a6105156eed3451619abf820c5e34a0e'),
            'LTC': (2413782, 'd89ee7a66506f97ceca7a40b2b853ac2d7260f78cff754467219d252e89b5a65'),
            'PIVX': (3726151, '6e248221277662fd0fc4758ef14dc5c86b30d5cf0687a6b544a76f20e279470a'),
            'SYS': (1556147, '481eca73fe77bd5c93a795f39d9ee6161bf7fd90d854649a992527070b5ca9e1')},
        'url_node3': {
            'BLOCK': (2874546, 'ccc'),
            'DASH': (1813785, '000000000000002dadab73fb1880a606a6105156eed3451619abf820c5e34a0e'),
            'LTC': (2413782, 'd89ee7a66506f97ceca7a40b2b853ac2d7260f78cff754467219d252e89b5a65'),
            'PIVX': (3726151, '6e248221277662fd0fc4758ef14dc5c86b30d5cf0687a6b544a76f20e279470a'),
            'SYS': (1556147, '481eca73fe77bd5c93a795f39d9ee6161bf7fd90d854649a992527070b5ca9e1')},
        'url_node4': {'BLOCK': (None, None), 'DASH': (None, None), 'DOGE': (None, None),
                      'LTC': (None, None), 'PIVX': (None, None), 'SYS': (None, None)}
    }
    ip_addresses = []
    for ip in my_dict.keys():
        ip_addresses.append(ip)
    return my_dict


def getblockhash(ip, coin, blockcount):
    url = ip + "xr/" + coin + "/xrgetblockhash"
    try:
        response = requests.post(url, json=[blockcount], timeout=30)
        test = response.json()
    except requests.exceptions.JSONDecodeError:
        result = response.text.replace(" ", "")
        # print("getblockhash", ip, coin, blockcount, result)
    else:
        result = None
    return result


def get_heights(ip):
    url = ip + "xrs/heights"
    try:
        response = requests.get(url, timeout=30)
        blockchain_length = response.json()
        blockchain_lengths[ip] = blockchain_length
    except requests.exceptions.RequestException as e:
        print(f"Failed to get data from {url}. Error: {e}")
        blockchain_lengths[ip] = None


# if blockchain_lengths:
#     url = ip + "xr/" + "getblockhash"
#     # response =  requests.get(url ,timeout=20)
#     requests.post(url, json=[blockchain_length], timeout=60)

while 1:
    ### REAL USE
    # GET HEIGHTS FROM ALL SERVERS
    blockchain_lengths = {}
    block_hashs = {}
    threads = []
    for ip in ip_addresses:
        t = Thread(target=get_heights, args=(ip,))
        threads.append(t)
        t.start()
    # wait for the threads to complete
    for t in threads:
        t.join()

    # blockchain_lengths = fake_data()

    # Print all the blockchain lengths
    for ip, lengths in blockchain_lengths.items():
        if lengths is not None:
            for coin in lengths.items():
                # print(coin[0], coin[1])
                # getblockhash(ip, coin[0], coin[1])
                blockchain_lengths[ip][coin[0]] = (blockchain_lengths[ip][coin[0]], getblockhash(ip, coin[0], coin[1]))
            print(f"Data received from {ip}")
        else:
            print(f"No data received from {ip}")
    print(blockchain_lengths)
    ### REAL USE
    # blockchain_lengths = fake_data()

    all_keys = set().union(*(d.keys() for d in blockchain_lengths.values() if d is not None))

    # Initialize the resolved data dictionary
    resolved_data = {}

    # Iterate through all keys
    snodes_count = len(ip_addresses)
    min_nodes_consensus = round(2 / 3 * snodes_count)
    print(f"total snodes_count: {snodes_count}\nmin_nodes_consensus: {min_nodes_consensus}")
    for key in all_keys:
        values = [blockchain_lengths[ip][key] if key in blockchain_lengths[ip] else (None, None) for ip in ip_addresses
                  if
                  blockchain_lengths[ip] is not None]
        # Determine the majority value for this key
        print('key', key, 'values:', values)
        counter_obj = Counter(values)
        most_comon = counter_obj.most_common()[0]
        # print("most_comon:", most_comon[0], most_comon[1])
        if (most_comon[1] >= min_nodes_consensus) & (snodes_count >= 3):
            resolved_data[key] = most_comon[0]
        else:
            resolved_data[key] = (None, None)
        print(f"consensus for key {key}: {resolved_data[key]}")

    print(f"Chain data: {resolved_data}")

    # Save data to log file
    data = {
        'timestamp': datetime.now().isoformat(),
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
    time.sleep(30)
