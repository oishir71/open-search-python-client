import csv
import logging
import os
import pprint
import sys

import stopwords_config
import urllib3
from dotenv import load_dotenv
from opensearchpy import OpenSearch

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
handler_format = logging.Formatter(
    "%(asctime)s : [%(name)s - %(lineno)d] %(levelname)-8s - %(message)s"
)
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)

load_dotenv()

urllib3.disable_warnings()


class OpenSearchClient:
    def __init__(self):
        self.client = OpenSearch(
            hosts=[{"host": "localhost", "port": 9200}],
            http_auth=("admin", os.environ["OPENSEARCH_INITIAL_ADMIN_PASSWORD"]),
            http_compress=True,
            use_ssl=True,
            verify_certs=False,
        )

    def get_plugins(self):
        return self.client.cat.plugins(format="json")

    def get_indices(self):
        return self.client.cat.indices(format="json")

    def create_index(self, index_name, settings):
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name, body=settings)
            logger.info(f"Index: {index_name} was created.")

    def get_stats(self, index_name: str):
        return self.client.stats(index=index_name)

    def analyze_text(self, index_name: str, text: str, analyzer: str = "standard"):
        return self.client.indices.analyze(
            index=index_name, body={"text": text, "analyzer": analyzer}
        )

    def insert_data(self, index_name: str, data: dict):
        self.client.index(index=index_name, body=data)

    def bulk_insert_data(self, index_name: str, data: list[dict]):
        for d in data:
            self.insert_data(index_name=index_name, data=d)

    def bulk_insert_data_by_csv(self, index_name: str, csv_file_path: str):
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.bulk_insert_data(index_name=index_name, data=reader)

    def search_data(self, index_name: str, query: dict):
        return self.client.search(index=index_name, body=query)

    def get_all_data(self, index_name: str, size: int = 100):
        return self.search_data(
            index_name=index_name, query={"query": {"match_all": {}}, "size": size}
        )


if __name__ == "__main__":
    index_name = "bookinfo-softreef-default"
    settings = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "unigram_cased_analyzer": {"tokenizer": "unigram_tokenizer"},
                    "unigram_uncased_analyzer": {
                        "tokenizer": "unigram_tokenizer",
                        "filter": ["lowercase"],
                    },
                    "ja_analyzer": {
                        "type": "custom",
                        "tokenizer": "kuromoji_tokenizer",
                    },
                    "ja_stop_analyzer": {
                        "type": "custom",
                        "tokenizer": "kuromoji_user_dict",
                        "mode": "search",  # ex. [関西国際空港] -> [関西, 関西国際空港, 国際, 空港]でセグメンテーション
                        "char_filter": [
                            "icu_normalizer",
                            "kuromoji_iteration_mark",
                        ],
                        "filter": [
                            "lowercase",
                            "kuromoji_baseform",
                            "kuromoji_number",
                            "kuromoji_stemmer",
                            # custom filter
                            "ja_part_of_speech",  # 名詞/形容詞/動詞のみ利用
                            "ja_stop_words",
                        ],
                    },
                },
                "tokenizer": {
                    "unigram_tokenizer": {
                        "type": "ngram",
                        "min_gram": 1,
                        "max_gram": 1,
                    },
                    "kuromoji_user_dict": {
                        "type": "kuromoji_tokenizer",
                        "user_dictionary_rules": stopwords_config.ja_user_dictionary_rules,
                    },
                },
                "filter": {
                    "ja_part_of_speech": {
                        "type": "kuromoji_part_of_speech",
                        "stoptags": stopwords_config.ja_stop_tags,
                    },
                    "ja_stop_words": {
                        "type": "ja_stop",
                        "stopwords": stopwords_config.ja_stopwords,
                    },
                },
            },
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "bookName": {
                    "type": "text",
                    "analyzer": "unigram_cased_analyzer",
                    "fields": {
                        "unanalyzed": {
                            "type": "keyword",
                        },
                        "tokenized_stop": {
                            "type": "text",
                            "analyzer": "ja_stop_analyzer",
                            "fielddata": True,
                        },
                    },
                },
                "description": {
                    "type": "text",
                    "analyzer": "unigram_cased_analyzer",
                    "fields": {
                        "unanalyzed": {
                            "type": "keyword",
                        },
                        "tokenized": {
                            "type": "text",
                            "analyzer": "ja_analyzer",
                            "fielddata": True,
                        },
                        "tokenized_stop": {
                            "type": "text",
                            "analyzer": "ja_stop_analyzer",
                            "fielddata": True,
                        },
                    },
                },
                "publicationDate": {
                    "type": "date",
                },
            },
        },
    }

    client = OpenSearchClient()
    client.create_index(index_name, settings)
    # client.bulk_insert_data_by_csv(
    #     index_name=index_name,
    #     csv_file_path=os.path.join(
    #         os.path.dirname(os.path.abspath(__file__)), "../data/bookdata.csv"
    #     ),
    # )
    # client.insert_data(
    #     index_name=index_name,
    #     data={
    #         "id": "a0013",
    #         "bookName": "水滸伝",
    #         "description": "水滸伝は中国の四大奇書の一つである。",
    #         "publicationDate": "2021-01-01",
    #     },
    # )
    client.search_data(index_name, query={"query": {"match": {"description": "水"}}})
    pprint.pprint(client.get_all_data(index_name))

    logger.info("--- これはテストです。 ---")
    response = client.analyze_text(
        index_name, "これはテストです。", analyzer="ja_stop_analyzer"
    )
    for token in response["tokens"]:
        logger.info(
            f"Token: {token['token']}, Start Offset: {token['start_offset']}, "
            f"End Offset: {token['end_offset']}, type: {token['type']}, position: {token['position']}"
        )

    logger.info("--- ｺﾚﾊﾃｽﾄﾃﾞｽ ---")
    response = client.analyze_text(index_name, "ｺﾚﾊﾃｽﾄﾃﾞｽ", analyzer="ja_stop_analyzer")
    for token in response["tokens"]:
        logger.info(
            f"Token: {token['token']}, Start Offset: {token['start_offset']}, "
            f"End Offset: {token['end_offset']}, type: {token['type']}, position: {token['position']}"
        )

    logger.info("--- ｔｈｉｓ　ｉｓ　ａ　ｔｅｓｔ ---")
    response = client.analyze_text(
        index_name, "ｔｈｉｓ　ｉｓ　ａ　ｔｅｓｔ", analyzer="ja_stop_analyzer"
    )
    for token in response["tokens"]:
        logger.info(
            f"Token: {token['token']}, Start Offset: {token['start_offset']}, "
            f"End Offset: {token['end_offset']}, type: {token['type']}, position: {token['position']}"
        )
