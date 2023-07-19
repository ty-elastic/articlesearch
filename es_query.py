import os
from elasticsearch import Elasticsearch
from elasticsearch.client import MlClient

ARTICLES_INDEX="articles"

def ask_question(context, question):

    url = f"https://{os.getenv('ES_USER')}:{os.getenv('ES_PASS')}@{os.getenv('ES_ENDPOINT')}:443"
    with Elasticsearch([url], verify_certs=True) as es:
        ml = MlClient(es)

        config = {"question_answering": {
        "question": question
        }}

        res = ml.infer_trained_model(model_id="deepset__roberta-base-squad2", docs=[{ "text_field": context}], inference_config=config)
        print(res)


def get_sources():
    url = f"https://{os.getenv('ES_USER')}:{os.getenv('ES_PASS')}@{os.getenv('ES_ENDPOINT')}:443"
    with Elasticsearch([url], verify_certs=True) as es:
        aggs = {
            "sources" : {
                "terms" : { "field" : "source",  "size" : 100 }
            }
        }

        fields = ["source"]
        resp = es.search(index=ARTICLES_INDEX,
                            aggs=aggs,
                            fields=fields,
                            size=1,
                            source=False)
        if len(resp['aggregations']['sources']) > 0:
            sources = []
            for bucket in resp['aggregations']['sources']['buckets']:
                sources.append(bucket['key'])
            print(sources)
            return sources
        else:
            return None

# Search ElasticSearch index and return body and URL of the result
def search(query_text):

    url = f"https://{os.getenv('ES_USER')}:{os.getenv('ES_PASS')}@{os.getenv('ES_ENDPOINT')}:443"
    with Elasticsearch([url], verify_certs=True) as es:

        fields = ["title", "text", "url", "figures.url", "figures.text"]

        search_results = es.search(
            index=ARTICLES_INDEX,
            query={
                "bool": {
                    "should": [
                        {
                            "text_expansion": {
                                "text_elser.tokens": {
                                    "model_id": ".elser_model_1",
                                    "model_text": query_text
                                }
                            }
                        },
                        {
                            "text_expansion": {
                                "title_elser.tokens": {
                                    "model_id": ".elser_model_1",
                                    "model_text": query_text
                                }
                            }
                        }
                    ]
                }
            },
            fields=fields,
            size=1,
            source=False
        )

        body = search_results['hits']['hits'][0]['fields']['text'][0]
        title = search_results['hits']['hits'][0]['fields']['title'][0]
        url = search_results['hits']['hits'][0]['fields']['url'][0]

        print(search_results)

        figures = []
        if 'figures.url' in search_results['hits']['hits'][0]['fields']:
            for i, fig in enumerate(search_results['hits']['hits'][0]['fields']['figures.url']):
                caption = search_results['hits']['hits'][0]['fields']['figures.text'][i]
                figures.append({"url": fig, "caption":caption})

        return title, body, url, figures
