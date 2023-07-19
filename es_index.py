import requests
from bs4 import BeautifulSoup
from es_bulk import bulkLoadIndexPipeline
import re
import urllib

ARTICLES_INDEX="articles"
ARTICLES_PIPELINE = "articles-embeddings"

HTTP_HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

def add_docs(docs):
    batch = []
    for doc in docs:
        batch.append(doc)
        if len(batch) >= 100:
            bulkLoadIndexPipeline(batch,ARTICLES_INDEX,ARTICLES_PIPELINE)
            batch = []
    bulkLoadIndexPipeline(batch,ARTICLES_INDEX,ARTICLES_PIPELINE)

def index_article(url, source):


    page = requests.get(url, timeout=30, headers=HTTP_HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="article")

    title = soup.find("title")
    title_text =title.text.strip()

    children = results.find_all("p", {"class":"image_center"})
    figures = {}
    for child in children:
        fig = {}
        #text = child.text.strip()
        images = child.findChildren("img")
        for img in images:
            #print(img['src'])
            fig["url"] = "https:" + img['src']
        spans = child.findChildren("span")
        for span in spans:
             text = child.text.strip()
             fig["text"] = text
             print(text)
             res = re.search(r'(Figure \d+)',text)
             if res != None:
                print("F"+res.group())
                figures[res.group()] = fig
        # if text.startswith("Figure") == True:
        #     print("yeah")
        #     figures[text] = last_image

    print(figures)

    children = results.findChildren("p")
    docs = []
    current_doc = {"source":source, "url": url, "text":"", "title":title_text, "figures.url":[], "figures.text":[]}

    for child in children:
        if child.has_attr("class"):
            #print(child["class"])
            if child["class"][0] == "image_center":
                #print("IMG"+child.text.strip())
                continue
        child_text = child.text.strip()
        if len(current_doc['text'])+ len(child_text) > 512:
            current_doc['text'] = current_doc['text'].strip()
            docs.append(current_doc)
            current_doc = {"url": URL, "text":"", "title":title_text, "figures.url":[], "figures.text":[]}
        current_doc['text'] = current_doc['text'] + " " + child_text
        figstart = child_text.find("Figure")
        if figstart != -1:
            sub = child_text[figstart:]
            res = re.findall(r'(Figure \d+)',sub)
            for match in res:
                print(match)
                if match in figures:
                    current_doc['figures.url'].append(figures[match]['url'])
                    current_doc['figures.text'].append(figures[match]['text'])
            
            #print(current_doc['figure'])

    
    print(docs)
    return docs

def crawl_articles(url, aref_class, source):
    parsed_url = urllib.parse.urlparse(url)

    page = requests.get(url, timeout=30, headers=HTTP_HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.findAll("a", {"class": aref_class})
    for result in results:
        url_path = urllib.parse.urlparse(result['href'])
        url_to_index = parsed_url.scheme + "://" + parsed_url.netloc + url_path.path
        print (f"indexing: {url_to_index}")
        docs = index_article(url_to_index, source)
        add_docs(docs)