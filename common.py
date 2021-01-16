import typing
import ytmusicapi
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

def create_ytmusic_url(album, track):
    return YTMusicResult(
        album["title"],
        track["title"],
        "https://music.youtube.com/browse/{}".format(album["browseId"]),
        "https://music.youtube.com/watch?v={}".format(track["videoId"])
    )

def get_browse_id(s):
    m = re.search("browse/([^/]*)/?$", s)
    if m:
        return m.group(1)
    return None

album_detail_cache = {}
def get_album_detail(yt, browseId):
    if browseId not in album_detail_cache:
        album_detail_cache[browseId] = yt.get_album(browseId)
    return album_detail_cache[browseId]
