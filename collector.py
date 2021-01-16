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

def str_similarity(a,b):
    return difflib.SequenceMatcher(None, a, b).ratio()

is_debug = True

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

def normalize(s):
    # unicode正規化
    s = unicodedata.normalize('NFKC', s)
    # 大文字小文字
    s = s.lower()
    # ~と～の表記ゆれ
    s = s.replace('~',' ').replace('\u301C',' ').replace('\uFF5E',' ')
    # (ZYTOKINE)の削除（SOUND HOLIC対応）
    s = s.replace('(zytokine)','')
    # (つぅ →(への変換(toho euro trigger対応)
    s = s.replace('(つぅ ','(')
    # (配信Ver)削除(凋叶棕対応)
    s = s.replace('(配信ver)','')
    # (feat.～)の削除（主にSOUND HOLIC対応）
    s = re.sub('\(feat\.[^(]*\)',"",s)
    # ()のあるなし
    s = s.replace('(','').replace(')','').replace('（','').replace('）','')
    s = s.replace('[','').replace(']','')
    # EPの削除（EP系対応）
    s = re.sub("-? *ep$", " ", s)
    # Singleの削除（Single系対応）
    s = re.sub("-? *single$", " ", s)
    # 空白のあるなし
    s = s.replace(' ','').replace('　','')
    return s

#EDIT_DISTANCE_THRES = 100
def find_track_in_albums(yt, seed, albums):
    album_found = False
    # album名のsimilarityが高いものから調べる
    norm_collection_name = normalize(seed.collection_name)
    albums = sorted(albums, key=lambda x:str_similarity(normalize(x["title"]), norm_collection_name), reverse=True)
    for album in albums:
        if is_debug:
            pass
            #pprint(album)
        # apple musicでのアーティスト名は必ずしもyoutube musicと一致しない。そのためアーティスト名の判定はしない
        # 例： 「蓬莱人形 ~ Dolls in Pseudo Paradise」のアルバムアーティストは「ZUN」ではなく「上海アリス幻樂団」
        norm_album_title = normalize(album["title"])
        if is_debug:
            pprint(norm_album_title)
            pprint(norm_collection_name)
            pprint(str_similarity(norm_album_title, norm_collection_name))
        # ときどき片方に含まれてない文字列がアルバムタイトルに混ざるので類似度緩めに設定
        if norm_album_title == norm_collection_name or str_similarity(norm_album_title, norm_collection_name) > 0.1:
            album_found = True
            album_detail = get_album_detail(yt, album["browseId"])
            if is_debug:
                pprint(album_detail)
            max_similarity = -1
            max_similarity_track = None
            for track in album_detail["tracks"]:
                if normalize(track["title"]) == normalize(seed.track_name) and track["index"] == seed.track_number:
                    return create_ytmusic_url(album, track)
                similarity = str_similarity(normalize(track["title"]), normalize(seed.track_name))
                if is_debug:
                    print("{}: similarity between {} and {}: {}".format(datetime.now(),normalize(track["title"]), normalize(seed.track_name),similarity))
                if similarity > max_similarity:
                    max_similarity = similarity
                    max_similarity_track = track
            # 正規化での一致で見つからなかったら類似度最大のものを採用。
            # アルバム名が一致している時点でトラックのどれかに合致する可能性が高いという仮定をしている
            if max_similarity_track is not None and max_similarity > 0.5:
                return create_ytmusic_url(album, max_similarity_track)
    if not album_found:
        print("{}: album not found:{}".format(datetime.now(), seed))
    return None

def search_ytmusic(yt:ytmusicapi.YTMusic, seed:Seed):
    # 該当するアルバムを見つける→該当する曲を見つける
    albums = get_albums(yt, seed.collection_name + " " + seed.artist_name)
    track = find_track_in_albums(yt, seed, albums)
    if track is not None:
        return track
    # アルバムアーティスト != アーティストの場合、アーティスト名を含めた検索がヒットしないことがある
    # その場合はアルバム名のみで再検索
    albums = get_albums(yt, seed.collection_name)
    track = find_track_in_albums(yt, seed, albums)
    if track is not None:
        return track
    return None


SLEEP_SECONDS=1
SLEEP_COUNT=100
def main():
    print("{}: start collector".format(datetime.now()))
    # languageをjaにしない場合日本語のアルバム名でも英語で返ってくる。そのため明示的に指定している
    yt = ytmusicapi.YTMusic("header_auth.json", language="ja")
    seed_file = "seed.tsv" if not is_debug else "seed2.tsv"
    with open(seed_file, encoding="utf-8") as f_in, open("result.tsv","wt", encoding="utf-8") as f_out:
        is_header = True
        i = 0
        output_header(f_out)
        for line in f_in:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed = Seed._make(line.rstrip().split("\t"))
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
            #if i > 1000:
            #    break
    print("{}: end collector".format(datetime.now()))

if __name__ == "__main__":
    main()
