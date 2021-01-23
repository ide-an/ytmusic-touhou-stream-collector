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

def normalize(s):
    # unicode正規化
    s = unicodedata.normalize('NFKC', s)
    # 大文字小文字
    s = s.lower()
    # ~と～の表記ゆれ
    s = s.replace('~',' ').replace('\u301C',' ').replace('\uFF5E',' ')
    # 全角括弧の対応
    s = s.replace('（ ','(').replace('） ',')')
    # (ZYTOKINE)の削除（SOUND HOLIC対応）
    s = s.replace('(zytokine)','')
    # (つぅ →(への変換(toho euro trigger対応)
    s = s.replace('(つぅ ','(')
    # (配信Ver)削除(凋叶棕対応)
    s = s.replace('(配信ver)','')
    # (feat.～)の削除（主にSOUND HOLIC対応）
    s = re.sub('\( *feat\.[^(]*\)',"",s)
    #  featの中に括弧があるケース（主にSOUND HOLIC対応）
    s = re.sub('\( *feat\.[^()]*\([^()]*\)[^(]*\)',"",s)
    # [feat.～]の削除（主にIOSYS対応）
    s = re.sub('\[ *feat\.[^\[]*\]',"",s)
    # (with ～)削除(幽閉サテライト対応)
    s = re.sub('\(with [^(]*\)',"",s)
    # [with ～]削除(幽閉サテライト対応)
    s = re.sub('\[with [^\[]*\]',"",s)
    # (op ver.)削除(幽閉サテライト対応)
    s = s.replace('(op ver.)','')
    # (~Mountain of Faith~)削除(the TOHO Creation EP 対応
    s = s.replace('( mountain of faith )','')
    # feat. cold kiss削除(ZYTOKINE対応)
    s = s.replace('feat. cold kiss','')
    # nana takahashi削除(ZYTOKINE対応)
    s = s.replace('nana takahashi','')
    # feat. chata削除(N+
    s = s.replace('feat.chata','')
    # / vo.～削除
    s = re.sub('/ *vo\..*$','', s)
    # IOSYS系削除
    s = s.replace('iosys hits punk covers','').replace('(karaoke ver)','')
    s = re.sub('\(イオシス東方コンピレーション[^)]*\)','', s)
    # 外柿山対応
    s = s.replace('変容する波形と位相。','')
    # ()のあるなし
    s = s.replace('(','').replace(')','')
    s = s.replace('[','').replace(']','')
    # EPの削除（EP系対応）
    s = re.sub("-? *ep *$", " ", s)
    # Singleの削除（Single系対応）
    s = re.sub("-? *single *$", " ", s)
    s = re.sub("-? *single *$", " ", s) # 幽閉サテライトなど２つ付いている場合がある
    # -ほげほげ- 削除
    s = re.sub(' -[^\-]*-','', s)
    # instrumental 削除（幽閉サテライトなど）
    s = s.replace('instrumental','')
    # remaster削除
    s = s.replace('remaster','')
    # ハイフンのあるなし
    s = s.replace('-',' ')
    # 空白のあるなし
    s = s.replace(' ','').replace('　','')
    return s

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
    old_search_key = search_key
    search_key = normalize_search_key(search_key)
    #if "NANA" in old_search_key:
    #    pprint(search_key)
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
        #if "NANA" in seed.collection_name:
        #    pprint((
        #        album["title"],
        #        album["artist"],
        #        seed.collection_name,
        #        seed.artist_name,
        #        str_similarity(normalize(album["title"]), normalize(seed.collection_name)),
        #        str_similarity(normalize(album["artist"]), normalize(seed.artist_name)),
        #    ))
        if str_similarity(normalize(album["title"]), normalize(seed.collection_name)) > 0.9 and str_similarity(normalize(album["artist"]), normalize(seed.artist_name)) > 0.7:
            return create_ytmusic_url(album, {"title":"","videoId":""})
    albums = get_albums(yt, seed.collection_name)
    for album in albums:
        #pprint(album)
        #if "NANA" in seed.collection_name:
        #    pprint((
        #        album["title"],
        #        album["artist"],
        #        seed.collection_name,
        #        seed.artist_name,
        #        str_similarity(normalize(album["title"]), normalize(seed.collection_name)),
        #        str_similarity(normalize(album["artist"]), normalize(seed.artist_name)),
        #    ))
        if str_similarity(normalize(album["title"]), normalize(seed.collection_name)) > 0.9 and str_similarity(normalize(album["artist"]), normalize(seed.artist_name)) > 0.7:
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
            #if i > 100:
            #    break
    print("{}: end collector".format(datetime.now()))

if __name__ == "__main__":
    main()
