import socket
from config import SERVER_HOST, SERVER_PORT, MODEL_PATH
from urllib.parse import urlparse
from os import path
from _thread import start_new_thread
import socket
import json
import pandas as pd
from helpers import is_what, split_url, split_param, create_path
import Stockings

def can_crawl(url, models):
    """
        Matches input URL against the pattern to determine if it can be crawled or not.
    """
    host = urlparse(url).netloc
    
    routes, params = split_url(url).values()

    try:
        tree = models[host]
    except KeyError:
        print("No data found for this host: ", host)
        return 'Yes'

    if len(tree) != 0 and url != '':
        url_params = {}
        found = False

        # TODO: modularize the below section to be reusable everywhere for searching

        for node_idx in range(0, len(tree)): # loop through all possible route paths
            node = tree[node_idx][str(node_idx)]
            equivalent = True
            if node['content_type'] != is_what(routes[0]):
                equivalent = False

            if node['len_content'] + 10 <= len(str(routes[0])):
                equivalent = False

            if node['len_route'] != (len(routes) - 1):
                equivalent = False
            else:
                for route in range(1, len(routes) - 1):
                    if node[str(route)]['content_type'] != is_what(routes[route]):
                        equivalent = False

            for idx, par in enumerate(params): #iterate through the parameters of the URL
                param = split_param(par)
                url_params[list(param)[0]] = param[list(param)[0]]

            for param_key in node['params'].keys():
                try:
                    url_params[param_key]
                except KeyError:
                    equivalent = False

            if equivalent is True:
                tree[node_idx][str(node_idx)]['len_equivalent'] += 1
                found = True
                break

        if found is False:
            return 'No'
        else:
            return 'Yes'
    else:
        return 'Yes'


def run(models):
    """
       An API server to interface with the crawler to respond with the given URL's crawlability.
    """

    server_socket = socket.socket()

    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
    except socket.error as err:
        print(str(err))

    server_socket.listen(5)

    print("Server started on port: ", SERVER_PORT)



    def threaded_crawler(conn):
        client = Stockings.Stocking(conn)
        while True:
            url = conn.read()
            if not url:
                break
            result = can_crawl(url, models)
            print(f"[{result}] Request recieved to crawl ", url)
            client.send(result)

        conn.close()

    while True:
        client, address = server_socket.accept()
        print('Crawler connected on :' + address[0] + ':' + str(address[1]))
        start_new_thread(threaded_crawler, (client, ))





if __name__ == '__main__':
    with open(MODEL_PATH, 'r') as file:
        models = json.loads(file.read())
    run(models)
