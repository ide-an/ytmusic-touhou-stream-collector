import ytmusicapi
import typing
from pprint import pprint
import re
from common import Seed, YTMusicResult, read_line, output_header, output_line, create_ytmusic_url, get_album_detail

def get_browse_id(s):
    m = re.search("browse/([^/]*)/?$", s)
    if m:
        return m.group(1)
    return None

def correct_result(yt:ytmusicapi.YTMusic, seed, ytm_result):
    if ytm_result.collection_view_url == "不明":
        # youtube musicにないやつ
        return None
    browse_id = get_browse_id(ytm_result.collection_view_url) 
    album_detail = get_album_detail(yt, browse_id)
    album_detail["browseId"] = browse_id
    track = [x for x in album_detail["tracks"] if x["index"] == seed.track_number][0]
    pprint(album_detail)
    pprint(track)
    return create_ytmusic_url(album_detail, track)

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
    i = 0
    with open("result.tsv",encoding="utf-8") as f_in, open("result_patched.tsv","wt",encoding="utf-8") as f_out:
        is_header = True
        output_header(f_out)
        for line in f_in:
            i+=1
            if i > 2000:
                break
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            seed, result = read_line(line)
            if seed in patches:
                result = correct_result(yt, seed, patches[seed])
            output_line(f_out, seed, result)

if __name__ == "__main__":
    main()
