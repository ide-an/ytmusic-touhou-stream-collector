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

def seed_v2_to_v1(columns):
    def a_or_b(a, b):
        if a is None or a == '':
            return b
        return a
    # jan	isrc	no	circle	spotify_album_artist_name	spotify_album_name	spotify_artist_name	spotify_track_name	spotify_album_url	spotify_track_url	apple_music_album_artist_name	apple_music_album_name	apple_music_artist_name	apple_music_track_name	apple_music_album_url	apple_music_track_url
    #print(columns)
    return Seed._make([
        a_or_b(columns[11], columns[5]), # collection_name:str
        a_or_b(columns[13], columns[7]), # track_name:str
        a_or_b(columns[12], columns[6]), # artist_name:str
        columns[2], # track_number:str
        'N/A', # release_date:str
        a_or_b(columns[14], columns[8]), # collection_view_url:str
        a_or_b(columns[15], columns[9]), # track_view_url:str
    ])

def seed_v3_to_v1(columns):
    # collection_name	track_name	artist_name	track_number	release_date	collection_view_url	track_view_url	spotify_collection_name	spotify_track_name	spotify_collection_view_url	spotify_track_view_url	amazon_music_collection_name	amazon_music_track_name	amazon_store_collection_view_url	amazon_music_collection_view_url	amazon_music_track_view_url
    return Seed._make([
        columns[0], # collection_name:str
        columns[1], # track_name:str
        columns[2], # artist_name:str
        columns[3], # track_number:str
        columns[4], # release_date:str
        columns[5], # collection_view_url:str
        columns[6], # track_view_url:str
    ])

def str_similarity(a,b):
    return difflib.SequenceMatcher(None, a, b).ratio()

is_debug = False

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
    # TAMUSIC対応
    s = re.sub('\(東方[^(]*\)',"",s)
    s = re.sub('\(touhou[^(]*\)',"",s)
    s = re.sub('\([^(]*string quartet\)',"",s)
    s = s.replace('(紅魔郷 妖々夢 永夜抄 best)','')
    s = s.replace('(妖精大戦争   東方三月精)','')
    s = s.replace('(violin+vocal project)','')
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

#EDIT_DISTANCE_THRES = 100
def find_track_in_albums(yt, seed, albums):
    album_found = False
    # album名のsimilarityが高いものから調べる
    norm_collection_name = normalize(seed.collection_name)
    albums = sorted(albums, key=lambda x:str_similarity(normalize(x["title"]), norm_collection_name), reverse=True)
    if is_debug:
        pprint([(x["title"],str_similarity(normalize(x["title"]), norm_collection_name)) for x in albums])
    for album in albums:
        if is_debug:
            #pass
            pprint(album)
        # apple musicでのアーティスト名は必ずしもyoutube musicと一致しない。そのためアーティスト名の判定はしない
        # 例： 「蓬莱人形 ~ Dolls in Pseudo Paradise」のアルバムアーティストは「ZUN」ではなく「上海アリス幻樂団」
        norm_album_title = normalize(album["title"])
        if is_debug:
            pprint(norm_album_title)
            pprint(norm_collection_name)
            pprint(str_similarity(norm_album_title, norm_collection_name))
        # アルバム名は完全一致とは限らないもののほぼ一致としたい
        if str_similarity(norm_album_title, norm_collection_name) > 0.8:
            album_found = True
            album_detail = get_album_detail(yt, album["browseId"])
            if is_debug:
                pprint(album_detail)
            track_num_estimate = 0
            for track in album_detail["tracks"]:
                track_num_estimate += 1
                if "index" in track and track["index"] != seed.track_number: # 同じ曲だけどトラック番号が違うというケースはあり得るがごく少ないのでpatch.tsvで拾う
                    continue
                if "index" not in track and str(track_num_estimate) != seed.track_number: # ytmがindexを返してくれないケースがあるので自前でtrack numberを求める
                    continue
                similarity = str_similarity(normalize(track["title"]), normalize(seed.track_name))
                if is_debug:
                    print("{}: similarity between {} and {}: {}".format(datetime.now(),normalize(track["title"]), normalize(seed.track_name),similarity))
                # アルバム名の一致条件が厳しめなのとトラック番号の一致を条件としているので、曲名の一致度の条件を緩める
                if similarity > 0.4:
                    return create_ytmusic_url(album, track)
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

def check_authorized(yt:ytmusicapi.YTMusic):
    # Cookieが壊れていると認証が切れていて検索結果が減少する
    # 例として蓬莱人形がヒットしなくなるので収集前に確認する
    results = yt.search("蓬莱人形", "albums", limit=100)
    for r in results:
        if r["title"] == "蓬莱人形 ~ Dolls in Pseudo Paradise":
            return True
    return False

SLEEP_SECONDS=1
SLEEP_COUNT=100
def main():
    print("{}: start collector".format(datetime.now()))
    # languageをjaにしない場合日本語のアルバム名でも英語で返ってくる。そのため明示的に指定している
    yt = ytmusicapi.YTMusic("header_auth.json", language="ja")
    if not(check_authorized(yt)):
        print("{}: NOT AUTHORIZED!!!".format(datetime.now()))
        return

    seed_file = "seed.tsv" if not is_debug else "seed2.tsv"
    with open(seed_file, encoding="utf-8") as f_in, open("result.tsv","wt", encoding="utf-8") as f_out:
        is_header = True
        i = 0
        output_header(f_out)
        for line in f_in:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed = seed_v3_to_v1(line.rstrip("\n").split("\t"))
            #seed = Seed._make(line.rstrip().split("\t")[:7])
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
