import re
import nltk
import scrapy
import string
import itertools
import webbrowser
import urllib.request
from elasticsearch import Elasticsearch
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors import LinkExtractor

nltk.download('stopwords')
from nltk.corpus import stopwords

class FinderSpider(CrawlSpider):
        name = 'finderspider'

        # collects data from the search "courses" query page, page by page.
        start_urls = ['https://www.essex.ac.uk/course-search?collection=uoe-courses-meta&query=courses&start_rank=%s' % page for page in range(1,557, 10)]

        doc_list = []

        # recursively calls the parse_item method, whenever a link of the specified domain is found
        rules = ( Rule(LinkExtractor(allow_domains=('essex.funnelback.co.uk')), callback='parse_items'),)

        # extracts richtext data from the div class
        def bundle_extractor(self, richtext):
                richtext_p = richtext.xpath('.//div[@class="richtext"]/p/text()').getall() 
                richtext_a = richtext.xpath('.//div[@class="richtext"]/a/text()').getall() 
                richtext_i = richtext.xpath('.//div[@class="richtext"]/i/text()').getall()
                richtext_span = richtext.xpath('.//div[@class="richtext"]/span/text()').getall()
                richtext_label = richtext.xpath('.//div[@class="richtext"]/label/text()').getall()
                richtext_li = richtext.xpath('.//div[@class="richtext"]/li/text()').getall()
                richtext_div = richtext.xpath('.//div[@class="richtext"]/div/text()').getall()
                
                bundle = richtext_p + richtext_a + richtext_i + richtext_span + richtext_label + richtext_li + richtext_div

                return bundle

        # handles the extraction of data from the document
        def parse_items(self, response):
                rand_dict = {}
                response.selector.remove_namespaces()   # removes namespace data from the document

                '''
                yield{ 'overview' : response.xpath('//span[@class="content-box__desc"]/text()').getall() }
                yield { 'overview_label' : response.xpath('//label[@class="content-box__label"]/text()').getall() }
                yield { 'rich' : richtext.xpath('//div[@class="richtext"]/text()').getall() }
                '''
                
                rand_dict['Full_Course_Name'] = response.xpath('//h1[@class="page-subtitle"]/text()').getall() # For Idenification Purposes (NOT TO BE MANIPULATED)
                rand_dict['title'] = response.xpath('//title/text()').getall()

                overview_description = response.xpath('//span[@class="content-box__desc"]/text()').getall()
                overview_label = response.xpath('//label[@class="content-box__label"]/text()').getall()

                # extracts the overview details from the webpage, depending on its existence.
                for x in range(len(overview_description)):
                        if 'Course' in overview_label[x]:
                                rand_dict['Course'] = overview_description[x]
                                
                        elif 'UCAS code' in overview_label[x]:
                                rand_dict['UCAS_code'] = overview_description[x]
                                
                        elif 'Start date' in overview_label[x]:
                                rand_dict['Start_date'] = overview_description[x]
                                
                        elif 'Study mode' in overview_label[x]:
                                rand_dict['Study_mode'] = overview_description[x]
                                
                        elif 'Duration' in overview_label[x]:
                                rand_dict['Duration'] = overview_description[x]
                                
                        elif 'Location' in overview_label[x]:
                                rand_dict['Location'] = overview_description[x]
                                
                        elif 'Based in' in overview_label[x]:
                                rand_dict['Based_in'] = overview_description[x]

                richtext = response.xpath('//div[@id="overview"]')
                richtext_bundle = self.bundle_extractor(richtext)
                rand_dict['overview'] = richtext_bundle

                richtext = response.xpath('//div[@id="entry-requirements"]')
                richtext_bundle = self.bundle_extractor(richtext)
                rand_dict['entry-requirements'] = richtext_bundle
                
                richtext = response.xpath('//div[@id="structure"]')
                richtext_bundle = self.bundle_extractor(richtext)       # calls the richtext extraction method
                rand_dict['structure'] = richtext_bundle
                
                richtext = response.xpath('//div[@id="fees-and-funding"]')
                richtext_bundle = self.bundle_extractor(richtext)
                rand_dict['fees-and-funding'] = richtext_bundle

                self.doc_list.append(rand_dict)

class Processor():
        
        def index(self):
                # initializes the crawler instance
                fs = FinderSpider()
                process = CrawlerProcess({
                    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
                })

                process.crawl(fs)
                process.start() # the script will block here until the crawling is finished
                process.join()

                # gets the list of webpage data
                doc_list = fs.doc_list

                # connects to the Elasticsearch host
                ES_HOST = {"host" : "localhost", "port" : 9200}
                es = Elasticsearch(hosts = [ES_HOST], timeout = 300)

                # deletes any old indexes named finderspider_index
                es.indices.delete(index='finderspider_index', ignore=[400, 404])

                # removes unneeded data from the index
                new_list = []
                for rand_dict in doc_list:
                
                        new_dict = {}
                        for name,item in rand_dict.items():
                                
                                if name == 'overview' or name == 'entry-requirements' or name == 'structure' or name == 'fees-and-funding' or name == 'title':
                                        # splits the list of multiple strings into single strings
                                        items = [w.split() for w in item]
                                        item_merge = list(itertools.chain(*items))      # combines lists into a flat list
                                        
                                        # convert to lower case
                                        tokens = [w.lower() for w in item_merge]

                                        # remove newlines and tabs from the document
                                        words = [re.sub(r"\s+", " ", w) for w in tokens]
                                        
                                        # remove speech punctuation
                                        words = [re.sub('[!?.,"|;)(£]', '', w) for w in words]
                                        words = [re.sub('[-/:]', ' ', w) for w in words] # splits words seperated by hyphens

                                        # Remove stop words
                                        stop_words = stopwords.words('english')
                                        words = [w for w in words if w not in stop_words]

                                        # remove duplicate, trailing & leading spaces
                                        words = [re.sub(' +', ' ', w) for w in words]
                                        words = [w.strip() for w in words]

                                        # removes empty entries in the list
                                        words = [w for w in words if (not w==" " and not w=="")]
                                
                                        new_dict[name] = words

                                elif name == 'Full_Course_Name':
                                        new_dict[name] = item

                                else:
                                        items = item.lower()
                                        items = re.sub('[!?.,"|;)(£]', '', items)
                                        items = re.sub('[-/:]', ' ', items)
                                        items = items.split()
                                        
                                        new_dict[name] = items

                        new_list.append(new_dict)

                # adds the document data to the index
                i = 0
                for docs in new_list:
                        res = es.index(index = "finderspider_index", doc_type = 'text', id = i, body = docs)
                        i = i + 1


                # deletes any old indexes named evaluation_index
                es.indices.delete(index='evaluation_index', ignore=[400, 404])

                # removes unneeded data from the index
                new_list = []
                for rand_dict in doc_list:
                
                        new_dict = {}
                        for name,item in rand_dict.items():
                                
                                if name == 'overview' or name == 'entry-requirements' or name == 'structure' or name == 'fees-and-funding' or name == 'title':
                                        # remove newlines and tabs from the document
                                        words = [re.sub(r"\s+", " ", w) for w in item]

                                        # remove duplicate, trailing & leading spaces
                                        words = [re.sub(' +', ' ', w) for w in words]
                                        words = [w.strip() for w in words]

                                        # removes empty entries in the list
                                        words = [w for w in words if (not w==" " and not w=="")]
                                
                                        new_dict[name] = words

                                else:
                                        new_dict[name] = item

                        new_list.append(new_dict)

                # adds the document data to the index
                i = 0
                for docs in new_list:
                        res = es.index(index = "evaluation_index", doc_type = 'text', id = i, body = docs)
                        i = i + 1

                # code below only works on local machines (Auto opens Kibana with pre-defined search filters) 
                '''
                # permalinks which will automatically set up kibana with the filters
                URL_1 = "http://localhost:5601/app/kibana#/discover/81ed2e60-4c20-11e9-b6b5-7bbaa984b4a1?_g=()"         # Finder Index
                URL_2 = "http://localhost:5601/app/kibana#/discover/76985fc0-4c21-11e9-b6b5-7bbaa984b4a1?_g=()"         # Evaluation Index

                # opens 2 browser tabs 
                webbrowser.open(URL_1)
                webbrowser.open(URL_2)
                '''

def main():
        pr = Processor()
        pr.index()

if __name__ == "__main__":
        main()



              
