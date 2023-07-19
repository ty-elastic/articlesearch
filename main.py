import argparse
import es_index

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--article", help="input url (single doc)")
    parser.add_argument("--crawl", help="url to crawl (multi-doc)")
    parser.add_argument("--crawl_aref_class", default="resultTitleLink", help="class of a references to crawl")

    parser.add_argument("source", help="document source")
    parser.add_argument("--disable_write", action='store_true', default=False, help="disable writing (test mode)")
    args = parser.parse_args()
    config = vars(args)
    print(config)
    process(args.article, args.crawl, args.crawl_aref_class, args.source, args.disable_write == False)

def process(article, crawl, crawl_aref_class, source, enable_write):
    es_index.crawl_articles(crawl, crawl_aref_class, source)

main()