# Webcrawler Search Engine (Elasticsearch Kibana)

## Explanation


## Platform Recommendation:
* This program has been run on Windows 10.0.15063 build 15063 and Mac OS X, developed using Python version 3.7, Elasticsearch 6.6.2 & Kibana 6.6.2, Other systems have not been tested, and it is advised to have caution with untested OS.

Python Library Dependencies 
* Nltk 
* Scrapy
* Pywin32
* Elasticsearch

## How to use the Program:
* How to scrape and index the courses offered by The University of Essex: 
  * Download and install Kibana 
  * Download and install Elasticsearch  
  * Run the *kibana.bat* file stored in the *C:/kibana/bin* path 
  * Check whether the [Kibana Server](http://localhost:5601) is running with the URL
  * Check whether the [Elasticsearch Server](http://localhost:9200) is running with the URL 
  * Using the python *pip installer*, install the following modules: 
    * Nltk 
    * Scrapy 
    * Pywin32 
    * Elasticsearch 
  * Run the python program on the command line, using the following command: 
    * python webcrawler_search.py 

* How to add the *finderspider_index* and the *evaluation_index* index patterns to Kibana: 
  * Visit the [Kibana Server](http://localhost:5601) URL
  * Locate the sidebar and click on management  
  * Under Kibana, click on Index Patterns  
  * Then click on the *create index pattern* button  
  * Type the name of the indices one by one, making sure to follow the next step procedure; Till both index patterns have been created. 
  
* How to add queries onto the Kibana discover page:  
  * Visit the [Kibana Server](http://localhost:5601) URL
  * Locate the sidebar and click on discover 
  * Click on the *Add a filter +* button, within the filter bar 
  * In the small overlay that pops up, click on the *Edit Query DSL* button 
  * Then open my *Elasticsearch Queries.txt* file and copy the query data under any of the numbers in the file  
  * Paste this data into the textbox provided in the overlay; Without forgetting to add the label data, which should be the number above the query you copied the data from.  
  * Repeat this for all ten queries

* How to disable or enable queries:  
  * Find the ‘filter bar’, located at the top of the Kibana discover web page. 
  * Hover your cursor over one of the filters, till a small menu pops up. 
  * Select enable filter button to view the documents retrieved using the filter. 
  * If you no longer wish to use the filter or want to view another filter, just follow the steps to disable the current filter first. Then access the new filter by enabling the next filter of choice.  
  **NOTE: Ensure that you have disabled the queries after use or the queries will stack up till there’s no longer any results.**

## Example Runtime
<pre>
C\...\webcrawler_search_py>python webcrawler_search.py
...
</pre>
