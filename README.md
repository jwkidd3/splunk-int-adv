# Splunk Int/Adv

## Setup: Choose your splunk implementation:
1. You can request a free eval splunk instance at https://www.splunk.com/en_us/download/splunk-cloud.html

2. Or you can run splunk in a Docker container (if you have docker on your machine): docker run -d -p 8000:8000 --platform linux/amd64  -e SPLUNK_GENERAL_TERMS=--accept-sgt-current-at-splunk-com -e SPLUNK_START_ARGS=--accept-license -e SPLUNK_PASSWORD=password --name splunk splunk/splunk:latest


## Data Load
Pull data from https://github.com/jwkidd3/splunk_int_adv_data <br>


Other files to load are generated from python scripts

Load based on table below:

| Index |   Type |                    SourceType  |      host(s)    |    Source (File)			 |
| ----- | ------ | -------------------------------| -------------| ----------------------|
| web		| Online Sales |		          access_combined_wcookie	|	segment in path 2|		access.zip   |
| security|	   Web Server		|            linux_secure	 |	  segment in path 2	|	secure.zip  |
| sales		 |    sales_entries |		        sales_entries |		  appserver |		sample_sales_entries_data.json  |
| sales		 |    retail_sales	|	          vendor_sales	|	  appserver |		vendor_sales.log  |
| network	|	   Web Security Appliance |	  cisco_wsa_squid |		webserver |		sample_cisco_wsa_sqid_data.json  |
| network	|	   firewall_data	|	        cisco_firewall |		firewall	|	sample_cisco_firewall_data.json  |


3. Before exercises can be done walk students through creating auto lookups for the following:
   | SourceType|Lookup File|LookupId|
   |-----------|-----------|--------|
   |access_combined_wcookie|products.csv|productId|
   |vendor_sales|products.csv|Code|
   |vendor_sales|vendors.csv|VendorID|


   *** NOTE: on all exercises and demos you may have to adjust timeframe to see data depending on when the last time data generation took place

   *** Remember, this is not a production environment. The UI for splunk changes on a semi regular basis and sometimes screenshots do not 100% match the product. Data for labs should be consistent but there are cicurmstanses where we will need to adapt an exercise based on data availability.
