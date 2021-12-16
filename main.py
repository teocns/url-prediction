from urllib.parse import urlparse
from os import path
from _thread import start_new_thread
import socket
import json
import pandas as pd
from helpers import is_what, split_url, split_param, create_path
from config import DATASET_PATH, MODEL_PATH, SERVER_HOST, SERVER_PORT


def create_model(train_data):
    """
        Create models(patterns) for each HOST by analysing the URL's routes and params.
    """

    tree = []

    for i in range(0, len(train_data['data'])): #Iterate through the URLs in the list
        routes, params = split_url(train_data['data'][i]['url']).values()
        scraped_jobs = train_data['data'][i]['scrapedJobs']
        url_params = {}

        if scraped_jobs != 0 and len(routes) != 0:

            if len(tree) != 0:
                found = False

                for n in range(0, len(tree)): # loop through all possible route paths
                    node = tree[n][n]
                    equivalent = True

                    if node['content_type'] != is_what(routes[0]):
                        equivalent = False

                    if node['len_content'] + 10 <= len(str(routes[0])):
                        equivalent = False

                    if node['len_route'] != (len(routes) - 1):
                        equivalent = False
                    else:
                        for route in range(1, len(routes) - 1):
                            if node[route]['content_type'] != is_what(routes[route]):
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
                        tree[n][n]['len_equivalent'] += 1
                        found = True
                        break

                if found is False:
                    tree = create_path(tree, routes, params, scraped_jobs)

            else:
                tree = create_path(tree, routes, params, scraped_jobs)

    return tree


def get_data():
    """
        Get the data by reading a file to create models by iterating trough the data.
    """

    model = {}
    url_data = pd.read_json(DATASET_PATH)

    for url_idx in range(0, len(url_data)):
        host = url_data['host'][url_idx]
        #total_urls = url_data['totalUrls'][url_idx]
        urls = json.loads(url_data['urls'][url_idx])

        train_data = {'host': host, 'data': urls}
        model[host] = create_model(train_data)

    model = json.dumps(model)

    with open(MODEL_PATH, 'w') as file:
        file.write(model)


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

def tcp_server(models):
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
        while True:
            data = conn.recv(2048)
            print("Request recieved to crawl", data.decode())
            if not data:
                break
            result = can_crawl(data.decode(), models)
            print(result)
            conn.sendall(result.encode())
        conn.close()

    while True:
        client, address = server_socket.accept()
        print('Crawler connected on :' + address[0] + ':' + str(address[1]))
        start_new_thread(threaded_crawler, (client, ))

    server_socket.close()


if __name__ == '__main__':
    if not path.exists(MODEL_PATH):
        print("Model not trained from dataset, training ....")
        get_data()
    with open(MODEL_PATH, 'r') as file:
        models = json.loads(file.read())
    tcp_server(models)
