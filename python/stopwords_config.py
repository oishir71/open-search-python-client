ja_user_dictionary_rules = [
    # format: "word,tokenize,reading,part of speech"
    "楽天モバイル,楽天モバイル,ラクテンモバイル,名詞-固有名詞-組織",
]

ja_stopwords = [
    # https://github.com/apache/lucene/blob/main/lucene/analysis/kuromoji/src/resources/org/apache/lucene/analysis/ja/stopwords.txt
    "_japanese_",  # default
]

ja_stop_tags = [
    "接頭詞",
    "接頭詞-名詞接続",
    "接頭詞-動詞接続",
    "接頭詞-形容詞接続",
    "接頭詞-数接続",
    "副詞",
    "副詞-一般",
    "副詞-助詞類接続",
    "連体詞",
    "感動詞",
    "未知語",
    "その他",
    "語断片",
    "未知語",
    "記号-アルファベット",
    # default
    "接続詞",
    "助詞",
    "助詞-格助詞",
    "助詞-格助詞-一般",
    "助詞-格助詞-引用",
    "助詞-格助詞-連語",
    "助詞-接続助詞",
    "助詞-係助詞",
    "助詞-副助詞",
    "助詞-間投助詞",
    "助詞-並立助詞",
    "助詞-終助詞",
    "助詞-副助詞／並立助詞／終助詞",
    "助詞-連体化",
    "助詞-副詞化",
    "助詞-特殊",
    "助動詞",
    "記号",
    "記号-一般",
    "記号-読点",
    "記号-句点",
    "記号-空白",
    "記号-括弧開",
    "記号-括弧閉",
    "その他-間投",
    "フィラー",
    "非言語音",
    # https://github.com/apache/lucene/blob/main/lucene/analysis/kuromoji/src/resources/org/apache/lucene/analysis/ja/stoptags.txt
]
