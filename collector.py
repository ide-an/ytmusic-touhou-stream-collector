import ytmusicapi
from pprint import pprint
import typing

class Seed(typing.NamedTuple):
    collection_name:str
    track_name:str
    artist_name:str
    track_numbe:str
    release_date:str
    collection_view_url:str
    track_view_url:str

def search_ytmusic(yt:ytmusicapi.YTMusic, seed:Seed):
    # 該当するアルバムを見つける→該当する曲を見つける
    albums = yt.search(seed.collection_name, 'albums')
    if len(albums) == 0:
        return None
    for album in albums:
        pprint(album)
        # apple musicでのアーティスト名は必ずしもyoutube musicと一致しない。そのためアーティスト名の判定はしない
        # 例： 「蓬莱人形 ~ Dolls in Pseudo Paradise」のアルバムアーティストは「ZUN」ではなく「上海アリス幻樂団」
        if album["title"] == seed.collection_name:
            album_detail = yt.get_album(album["browseId"])
            pprint(album_detail)
            for track in album_detail["tracks"]:
                #pprint(track)
                if track["title"] == seed.track_name:
                    # TODO: 整形
                    return track
    return None

def main():
    # languageをjaにしない場合日本語のアルバム名でも英語で返ってくる。そのため明示的に指定している
    yt = ytmusicapi.YTMusic(language="ja")
    with open("seed.tsv", encoding="utf-8") as f_in, open("result.tsv","wt", encoding="utf-8") as f_out:
        is_header = True
        i = 0
        for line in f_in:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed = Seed._make(line.rstrip().split("\t"))
            pprint(seed)
            # TODO: ytmusic apiを引いて該当する曲があるか確認
            result = search_ytmusic(yt, seed)
            if result is not None:
                pprint(result)
            # TODO: 結果出力
            i += 1
            if i > 1:
                break


if __name__ == "__main__":
    main()
