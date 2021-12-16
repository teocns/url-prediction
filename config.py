DATASET_PATH = './urls_dataset.json'
MODEL_PATH = './models.json'
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 4444


DATABASES = {
    "AWS_DASHBOARD": {
        "HOST": 'guided-crawler.cmu5pcc4huaw.eu-west-3.rds.amazonaws.com',
        "PORT": 3306,
        "USER": "admin",
        "PASS": '123Javier10!',
        "DB": "crawling",
        "POOL_SIZE": 32
    },
    "CRAWLER_CACHE": {
        "HOST": 'localhost',
        "PORT": 3306,
        "USER": "root",
        "PASS": '123Javier10!',
        "DB": "crawler",
        "POOL_SIZE": 8
    }
}
