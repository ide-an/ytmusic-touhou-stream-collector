import ytmusicapi
import typing
from pprint import pprint
import re

class Seed(typing.NamedTuple):
    collection_name:str
    track_name:str
    artist_name:str
    track_number:str
    release_date:str
    collection_view_url:str
    track_view_url:str

class YTMusicResult(typing.NamedTuple):
    collection_name:str
    track_name:str
    collection_view_url:str
    track_view_url:str

def read_line(line:str):
    cols = line.rstrip().split("\t")
    seed = Seed._make(cols[:7])
    result = YTMusicResult._make(cols[7:])
    return (seed, result)

def output_header(f_out):
    line = "\t".join([
        "collection_name",
        "track_name",
        "artist_name",
        "track_number",
        "release_date",
        "apple_collection_view_url",
        "apple_track_view_url",
        "youtube_collection_name",
        "youtube_track_name",
        "youtube_collection_view_url",
        "youtube_track_view_url",
    ])
    f_out.write(line + "\n")

def output_line(f_out, seed:Seed, ytmusic_result:YTMusicResult):
    line = "\t".join([
        seed.collection_name,
        seed.track_name,
        seed.artist_name,
        seed.track_number,
        seed.release_date,
        seed.collection_view_url,
        seed.track_view_url,
        ytmusic_result.collection_name if ytmusic_result is not None else "不明",
        ytmusic_result.track_name if ytmusic_result is not None else "不明",
        ytmusic_result.collection_view_url if ytmusic_result is not None else "不明",
        ytmusic_result.track_view_url if ytmusic_result is not None else "不明",
    ])
    f_out.write(line + "\n")

def get_browse_id(s):
    m = re.search("browse/([^/]*)/?$", s)
    if m:
        return m.group(1)
    return None

def create_ytmusic_url(browse_id, album, track):
    return YTMusicResult(
        album["title"],
        track["title"],
        "https://music.youtube.com/browse/{}".format(browse_id),
        "https://music.youtube.com/watch?v={}".format(track["videoId"])
    )

def correct_result(yt:ytmusicapi.YTMusic, seed, ytm_result):
    if ytm_result.collection_view_url == "不明":
        # youtube musicにないやつ
        return None
    browse_id = get_browse_id(ytm_result.collection_view_url) 
    album_detail = yt.get_album(browse_id)
    track = [x for x in album_detail["tracks"] if x["index"] == seed.track_number][0]
    return create_ytmusic_url(browse_id, album_detail, track)

def main():
    yt = ytmusicapi.YTMusic("header_auth.json", language="ja")
    patches = {}
    with open("patch.tsv",encoding="utf-8") as f_patch:
        is_header = True
        for line in f_patch:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed, result = read_line(line)
            patches[seed] = result

    #pprint(patches)
    with open("result.tsv",encoding="utf-8") as f_in, open("result_patched.tsv","wt",encoding="utf-8") as f_out:
        is_header = True
        output_header(f_out)
        for line in f_in:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed, result = read_line(line)
            if seed in patches:
                result = correct_result(yt, seed, patches[seed])
            output_line(f_out, seed, result)

if __name__ == "__main__":
    main()
