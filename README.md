Predicts which URLs to scrape based on past results.

Destructures routes to generate common patterns.

Supply a .json dataset of an array containing the following objects
{
  "host": "", // Domain name
  "urls": "[{\"url\": \"\", \"scrapedJobs\": 0 }]",
  "totalUrls": 0
}

Model will learn to recognize urls which in the past were containing "scrapedJobs": 1
