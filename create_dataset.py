from db import MysqlDatabase
from config import DATASET_PATH
import json


database = MysqlDatabase()


print ('Fetching results...')
import time
time.sleep(1)

results = database.query_db("""

select 
    host, 
    JSON_ARRAYAGG(JSON_OBJECT('url', url, 'scrapedJobs', total_scraped_jobs)) as urls,
    count(1) as totalUrls
from scraped_urls
group by host;
""")


print(f'Writing {len(results)} results to file {DATASET_PATH}')

with open(DATASET_PATH,'w+') as f:
    f.write(json.dumps(results))