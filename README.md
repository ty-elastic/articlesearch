# ArticleSearch

## Environment Variables
Ensure the following env variables are defined:
```
export ES_ENDPOINT=""
export ES_USER=""
export ES_PASS=""
export ELASTICSEARCH_URL="https://${ES_USER}:${ES_PASS}@${ES_ENDPOINT}:443"
```

If you want to bounce ES results off OpenAI for Q&A, ensure the following env variables are defined:
```
export OPENAI_API_KEY=""
export OPENAI_BASE=""
export OPENAI_DEPLOYMENT_ID=""
export OPENAI_MODEL=""
export OPENAI_API_VERSION=""
```

## Elasticsearch Setup
Ensure the following indices and pipelines are defined:

### Indices
```
curl -XDELETE "$ELASTICSEARCH_URL/articles" -H "kbn-xsrf: reporting"
curl -XPUT "$ELASTICSEARCH_URL/articles" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
"mappings": {
  "properties": {
    
    "title": {
      "type": "text"
    },
    "title_elser.tokens": {
        "type": "rank_features" 
    },
    "source": {
      "type": "keyword"
    },
    "url": {
      "type": "keyword"
    },
    "text": {
      "type": "text"
    },
    "text_elser.tokens": {
        "type": "rank_features" 
      }
  }
}
}
```

### Models

```
Q_AND_A_MODEL="deepset__roberta-base-squad2"
ELASTICSEARCH_URL="https://${ES_USER}:${ES_PASS}@${ES_ENDPOINT}:443"

git clone https://github.com/elastic/eland.git
docker build -t elastic/eland eland

sudo docker run -it --rm elastic/eland \
    eland_import_hub_model \
    --url $ELASTICSEARCH_URL \
    --hub-model-id deepset/roberta-base-squad2 \
    --clear-previous \
    --start

curl -XPUT "$ELASTICSEARCH_URL/_ml/trained_models/.elser_model_1" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
"input": {
    "field_names": ["text_field"]
}
}'
curl -XPOST "$ELASTICSEARCH_URL/_ml/trained_models/.elser_model_1/deployment/_start?deployment_id=for_search" -H "kbn-xsrf: reporting"

```

### Pipelines
```
curl -XDELETE "$ELASTICSEARCH_URL/_ingest/pipeline/articles-embeddings" -H "kbn-xsrf: reporting"
curl -XPUT "$ELASTICSEARCH_URL/_ingest/pipeline/articles-embeddings" -H "kbn-xsrf: reporting" -H "Content-Type: application/json" -d'
{
 "description": "Articles embedding pipeline",
 "processors": [
   {
      "inference": {
        "model_id": ".elser_model_1",
        "target_field": "text_elser",
        "field_map": { 
          "text": "text_field"
        },
        "inference_config": {
          "text_expansion": { 
            "results_field": "tokens"
          }
        }
      }
    },
    {
      "inference": {
        "model_id": ".elser_model_1",
        "target_field": "title_elser",
        "field_map": { 
          "text": "text_field"
        },
        "inference_config": {
          "text_expansion": { 
            "results_field": "tokens"
          }
        }
      }
    }
 ],
 "on_failure": [
   {
     "set": {
       "description": "Index document to '\''failed-<index>'\''",
       "field": "_index",
       "value": "failed-{{{_index}}}"
     }
   },
   {
     "set": {
       "description": "Set error message",
       "field": "ingest.failure",
       "value": "{{_ingest.on_failure_message}}"
     }
   }
 ]
}'
```

## Use

```
python main.py --crawl_url (URL TO CRAWL) --crawl_aref_class (CLASS OF ARTICLES) --source (SOURCE OF DOCUMENTS) --article_section_class (CLASS OF BODY IN ARTICLES)
```