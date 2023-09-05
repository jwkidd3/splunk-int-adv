# Splunk Int/Adv

## Setup: Choose your splunk implementation:
1. You can request a free eval splunk instance at https://www.splunk.com/en_us/download/splunk-cloud.html

2. Or you can run splunk in a Docker container (if you have docker on your machine): docker run -d -p 8000:8000 -e "SPLUNK_START_ARGS=--accept-license" --platform linux/amd64 -e "SPLUNK_PASSWORD=password" --name splunk splunk/splunk:latest

### Original data sources:
https://docs.splunk.com/images/Tutorial/tutorialdata.zip <br>
https://docs.splunk.com/images/d/db/Prices.csv.zip <br>
http://splk.it/f1data

## Data Load
There are 4 indexes in this class: web, security, sales and network <br>
Pull data from https://docs.splunk.com/images/Tutorial/tutorialdata.zip <br>
Split the zip file into the access logs and the secure logs and separate out the vendors sales data. <br>

Also pull data from http://splk.it/f1data. Only log file you want from this is linux_s_30DAY.log

Other files to load are generated from python scripts

Load based on table below:

| Index |   Type |                    SourceType  |      host(s)    |    Source (File)			 |
| ----- | ------ | -------------------------------| -------------| ----------------------|
| Web		| Online Sales |		          access_combined	|	webserver|		access logs (3)   |
| Security|	   Web Server		|            linux_secure	 |	  webserver	|	secure.log (3)  |
| Sales		 |    sales_entries |		        sales_entries |		  appserver |		sample_sales_entries_data.json  |
| Sales		 |    retail_sales	|	          vendor_sales	|	  appserver |		vendor_sales.log  |
| Network	|	   Web Security Appliance |	  cisco_wsa_squid |		webserver |		sample_cisco_wsa_sqid_data.json  |
| Network	|	   firewall_data	|	        cisco_firewall |		firewall	|	sample_cisco_firewall_data.json  |


3. Before exercises can be done walk students through creating auto lookups for the following:
   | SourceType|Lookup File|LookupId|
   |-----------|-----------|--------|
   |access_combined*|products.csv|productId|
   |vendor_sales|products.csv|Code|
   |vendor_sales|vendors.csv|VendorID|


   ***NOTE: on all exercises and demos you may have to adjust timeframe to see data depending on when the last time data generation took place
