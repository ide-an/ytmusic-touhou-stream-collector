import ytmusicapi
from pprint import pprint
import typing
from time import sleep
from datetime import datetime
import unicodedata
import re

is_debug = False

class Seed(typing.NamedTuple):
    collection_name:str
    track_name:str
    artist_name:str
    track_numbe:str
    release_date:str
    collection_view_url:str
    track_view_url:str

class YTMusicResult(typing.NamedTuple):
    collection_view_url:str
    track_view_url:str

def create_ytmusic_url(album, track):
    return YTMusicResult(
        "https://music.youtube.com/browse/{}".format(album["browseId"]),
        "https://music.youtube.com/watch?v={}".format(track["videoId"])
    )

albums_cache = {}
def get_albums(yt, collection_name, artist_name):
    # マイナス検索にならないようにハイフンを置換
    search_key = (collection_name).replace("-", " ")
    # EPの削除（狐夢想屋対応）
    search_key = re.sub("EP$", "", search_key)
    if is_debug:
        print("{}: search_key:{}".format(datetime.now(), search_key))
    if search_key not in albums_cache:
        # TODO: 検索結果が複数ページの場合の対処
        albums_cache[search_key] = yt.search(search_key, 'albums', limit=100)
    return albums_cache[search_key]

album_detail_cache = {}
def get_album_detail(yt, browseId):
    if browseId not in album_detail_cache:
        album_detail_cache[browseId] = yt.get_album(browseId)
    return album_detail_cache[browseId]

def normalize(s):
    # unicode正規化
    s = unicodedata.normalize('NFKC', s)
    # 大文字小文字
    s = s.lower()
    # ~と～の表記ゆれ
    s = s.replace('~',' ').replace('\u301C',' ').replace('\uFF5E',' ')
    # ()のあるなし
    s = s.replace('(','').replace(')','').replace('（','').replace('）','')
    s = s.replace('[','').replace(']','')
    # 空白のあるなし
    s = s.replace(' ','').replace('　','')
    # EPの削除（狐夢想屋対応）
    s = re.sub("-ep$", "", s)
    return s

def search_ytmusic(yt:ytmusicapi.YTMusic, seed:Seed):
    # 該当するアルバムを見つける→該当する曲を見つける
    albums = get_albums(yt, seed.collection_name, seed.artist_name)
    album_found = False
    for album in albums:
        if is_debug:
            pprint(album)
        # apple musicでのアーティスト名は必ずしもyoutube musicと一致しない。そのためアーティスト名の判定はしない
        # 例： 「蓬莱人形 ~ Dolls in Pseudo Paradise」のアルバムアーティストは「ZUN」ではなく「上海アリス幻樂団」
        if is_debug:
            pprint(normalize(album["title"]))
            pprint(normalize(seed.collection_name))
        if normalize(album["title"]) == normalize(seed.collection_name):
            album_found = True
            album_detail = get_album_detail(yt, album["browseId"])
            if is_debug:
                pprint(album_detail)
            for track in album_detail["tracks"]:
                #pprint(track)
                if normalize(track["title"]) == normalize(seed.track_name):
                    return create_ytmusic_url(album, track)
    if not album_found:
        print("{}: album not found:{}".format(datetime.now(), seed))
    return None

def output_line(f_out, seed:Seed, ytmusic_result:YTMusicResult):
    line = "\t".join([
        seed.collection_name,
        seed.track_name,
        seed.artist_name,
        seed.track_numbe,
        seed.release_date,
        seed.collection_view_url,
        seed.track_view_url,
    ])
    if ytmusic_result is None:
        line += "\tNone\tNone"
    else:
        line += "\t{}\t{}".format(
            ytmusic_result.collection_view_url,
            ytmusic_result.track_view_url
        )
    f_out.write(line + "\n")

SLEEP_SECONDS=1
SLEEP_COUNT=100
def main():
    print("{}: start collector".format(datetime.now()))
    # languageをjaにしない場合日本語のアルバム名でも英語で返ってくる。そのため明示的に指定している
    yt = ytmusicapi.YTMusic("header_auth.json", language="ja")
    with open("seed.tsv", encoding="utf-8") as f_in, open("result.tsv","wt", encoding="utf-8") as f_out:
        is_header = True
        i = 0
        for line in f_in:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed = Seed._make(line.rstrip().split("\t"))
            if is_debug:
                pprint(seed)
            result = search_ytmusic(yt, seed)
            output_line(f_out, seed, result)
            i += 1
            if i%SLEEP_COUNT == 0:
                print("{}: done {} songs...".format(datetime.now(), i))
                sleep(SLEEP_SECONDS)
            if i > 1000:
                break
    print("{}: end collector".format(datetime.now()))

if __name__ == "__main__":
    main()
