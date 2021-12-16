from config import DATASET_PATH, MODEL_PATH
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





print(f"Training model from {DATASET_PATH}...")
get_data()