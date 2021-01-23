import ytmusicapi
from pprint import pprint
import typing
from time import sleep
from datetime import datetime
import unicodedata
import re
import difflib
import traceback
from common import Seed, YTMusicResult, create_ytmusic_url, output_line, output_header, get_album_detail

is_debug = False

def str_similarity(a,b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def normalize_search_key(search_key):
    # マイナス検索にならないようにハイフンから始まるトークンを置換
    search_key = re.sub('(^| )-',' ',search_key)
    # EPの削除（狐夢想屋などEP系対応）
    search_key = re.sub(" EP($| )", " ", search_key)
    # Singleの削除（Single系対応）
    search_key = re.sub("Single($| )", " ", search_key)
    # (feat.～)の削除（主にSOUND HOLIC対応）
    search_key = re.sub('\(feat\.[^(]*\)',"",search_key)
    # ─削除(IOSYS対応)
    search_key = search_key.replace('─',' ')
    # with senya削除(幽閉サテライト対応)
    search_key = search_key.replace('with senya','')
    # ≒削除(Love≒Sick対応)
    search_key = search_key.replace('≒',' ')
    # ★☆削除(ROLLING★STAR, はくたく☆りぼん まじキモけーね 対応)
    search_key = search_key.replace('★',' ').replace('☆',' ')
    # ⇔♭削除(EnD ⇔ StarT,B♭: Scarlet Sequel 対応)
    search_key = search_key.replace('⇔',' ').replace('♭',' ')
    # カッコ囲み削除
    search_key = re.sub('\([^(]*\)',"",search_key)
    return search_key

albums_cache = {}
def get_albums(yt, search_key):
    search_key = normalize_search_key(search_key)
    if is_debug:
        print("{}: search_key:{}".format(datetime.now(), search_key))
    if search_key not in albums_cache:
        # TODO: 検索結果が複数ページの場合の対処
        albums_cache[search_key] = yt.search(search_key, 'albums', limit=100)
    return albums_cache[search_key]

def search_ytmusic(yt:ytmusicapi.YTMusic, seed:Seed):
    # 該当するアルバムを見つける→該当する曲を見つける
    albums = get_albums(yt, seed.collection_name + " " + seed.artist_name)
    for album in albums:
        #pprint(album)
        if str_similarity(album["title"], seed.collection_name) > 0.9 and str_similarity(album["artist"], seed.artist_name):
            return create_ytmusic_url(album, {"title":"","videoId":""})
    return None

SLEEP_SECONDS=1
SLEEP_COUNT=100
def main():
    print("{}: start collector".format(datetime.now()))
    # languageをjaにしない場合日本語のアルバム名でも英語で返ってくる。そのため明示的に指定している
    yt = ytmusicapi.YTMusic("header_auth.json", language="ja")
    seed_file = "albums.tsv"
    with open(seed_file, encoding="utf-8") as f_in, open("result2.tsv","wt", encoding="utf-8") as f_out:
        is_header = True
        i = 0
        output_header(f_out)
        for line in f_in:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            artist, album =line.rstrip().split("\t")
            seed = Seed(album, "", artist, "","","","")
            if is_debug:
                pprint(seed)
            try:
                result = search_ytmusic(yt, seed)
            except Exception as e:
                traceback.print_exc()
                result = None
            output_line(f_out, seed, result)
            i += 1
            if i%SLEEP_COUNT == 0:
                print("{}: done {} songs...".format(datetime.now(), i))
                sleep(SLEEP_SECONDS)
            #if i > 10:
            #    break
    print("{}: end collector".format(datetime.now()))

if __name__ == "__main__":
    main()
