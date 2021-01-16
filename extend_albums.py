import ytmusicapi
from pprint import pprint
import traceback
from common import Seed, YTMusicResult, read_line, output_header, output_line, create_ytmusic_url, get_album_detail, get_browse_id

def collect_artist_ids_from_album_ids(yt, album_ids):
    artist_ids = set()
    for album_id in album_ids:
        try:
            album_detail = get_album_detail(yt, album_id)
            artist_ids |= set(x["id"] for x in album_detail["artist"])
        except Exception as e:
            traceback.print_exc()
            print("album_id: {}".format(album_id))
    return artist_ids

def collect_album_ids_from_artist_ids(yt, artist_ids):
    def collect_artist_cds(artist, ty):
        result = set()
        if ty in artist:
            result |= set(x["browseId"] for x in artist[ty]["results"])
        if ty in artist and artist[ty]["browseId"]:
            #pprint(artist[ty])
            cds = yt.get_artist_albums(artist[ty]["browseId"],artist[ty]["params"])
            result |= set(x["browseId"] for x in cds)
        return result
    album_ids = set()
    for artist_id in artist_ids:
        try:
            artist = yt.get_artist(artist_id)
            album_ids |= collect_artist_cds(artist, "albums")
            album_ids |= collect_artist_cds(artist, "singles")
        except Exception as e:
            traceback.print_exc()
            print("artist_id: {}".format(artist_id))
    return album_ids

def main():
    yt = ytmusicapi.YTMusic("header_auth.json", language="ja")

    album_ids = set()
    i = 0
    with open("result_patched.tsv",encoding="utf-8") as f_in:
        is_header = True
        for line in f_in:
            i += 1
            if i > 100000:
                break
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed, result = read_line(line)
            if result.collection_view_url == "不明":
                continue
            browse_id = get_browse_id(result.collection_view_url)
            if browse_id:
                album_ids.add(browse_id)
    original_album_ids = album_ids

    for i in range(1):
        # albumからartistを収集
        artist_ids = collect_artist_ids_from_album_ids(yt, album_ids)
        # artistからalbumを収集
        new_album_ids = collect_album_ids_from_artist_ids(yt, artist_ids)
        if album_ids == new_album_ids:
            print("新しいアルバムがない")
            break
        album_ids = new_album_ids
    else:
        print("まだ新しいアルバムあるかもだが終了")

    pprint(len(original_album_ids))
    pprint(len(album_ids))
    diff_albums =  (album_ids - original_album_ids)
    pprint(len(diff_albums))
    with open("albums.tsv", "wt", encoding="utf-8") as f_out:
        for album_id in diff_albums: # 差分だけ出す。
            try:
                album_detail = get_album_detail(yt, album_id)
                f_out.write("\t".join([
                    ",".join(x["name"] for x in album_detail["artist"]),
                    ",".join(x["id"] for x in album_detail["artist"]),
                    album_id,
                    album_detail["title"],
                ]) + "\n")
            except:
                f_out.write("\t".join([
                    "???",
                    "???",
                    album_id,
                    "???",
                ]) + "\n")

if __name__ == "__main__":
    main()
