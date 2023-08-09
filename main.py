import argparse
import es_index

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--crawl_url", help="url to crawl (multi-doc)")
    parser.add_argument("--crawl_aref_class", default="newsreleaseconsolidatelink", help="class of a references to crawl")
    parser.add_argument("--article_section_class", default="release-body", help="class of a references to crawl")
    parser.add_argument("--source", help="document source")
    args = parser.parse_args()
    config = vars(args)
    print(config)
    process(args.crawl_url, args.crawl_aref_class, args.article_section_class, args.source)

def process(crawl_url, crawl_aref_class, article_section_class, source):
    es_index.crawl_articles(crawl_url, crawl_aref_class, article_section_class, source)

main()