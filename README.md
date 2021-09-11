# ytmusic-touhou-stream-collector

## What's this?

ytmusic-touhou-stream-collectorは[東方同人音楽流通](https://touhou-music.jp/)経由でYoutube Musicにストリーム配信されている東方アレンジを収集するスクリプトです。

出力結果は[google doc: 東方同人音楽流通 Apple Music + YouTube Music](https://docs.google.com/spreadsheets/d/1H9X67bJe-hWKFXn1w1gPFao3p3fykOGFQO_6eJY4Q34/edit?usp=sharing)に公開しています。

リストのシードデータとして @shiroemons氏による[AppleMusicの配信リスト](https://docs.google.com/spreadsheets/d/1h1M6Q0UPGvF8kTIiw0F5c7k0mGlkyhrI4kSkASRV_bw)を利用しています。

## How to run

### Set up

https://ytmusicapi.readthedocs.io/en/latest/setup.html#authenticated-requests を参考に`header_auth.json`を作成する。

### Run

```sh
# venv環境作成
python -m venv env
. env/Scripts/activate
# 必要なパッケージ入れる
pip install < requirements.txt
# 実行
python collector.py
# result.tsvに出力される
# 名寄誤りの修正ファイルを patch.tsvとして作成。フォーマットは後述。
ls patch.tsv

# patch.tsvによる修正の適用。result_patched.tsvに出力される
python patcher.py

# ytmのみにあるアルバム（シロ氏のリストにないもの）を追加
cat ytm_only.tsv >> result_patched.tsv

# diffを取りやすいようにsort
python sort.py result_patched.tsv result_patched_sorted.tsv

# archiveに保存
cp result_patched_sorted.tsv archive/result.tsv
sh split.sh
```

## patch.tsvのフォーマット

フォーマットはresult.tsvと同じTSV。
名寄の修正方法は以下の通り

### 対応するYoutube Musicのアルバムがあり、アルバムのトラック番号がApple Musicと同じ場合

 * `youtube_collection_view_url`

を対応するYoutube Musicのアルバムのcollection view urlにする。

例
```
collection_name	track_name	artist_name	track_number	release_date	apple_collection_view_url	apple_track_view_url	youtube_collection_name	youtube_track_name	youtube_collection_view_url	youtube_track_view_url
#GENSOKYOholoism	[Episode 0] Roujinkai hicchou, Inishie no Touhou arrange shibari utawaku	COOL&CREATE	1	2020-07-10 12:00:00 UTC	https://music.apple.com/jp/album/gensokyoholoism/1522016421?uo=4	https://music.apple.com/jp/album/episode-0-roujinkai-hicchou-inishie-no-touhou-arrange/1522016421?i=1522016422&uo=4	不明	不明	https://music.youtube.com/browse/MPREb_MVfGVRCy7Uv	不明
```

**TODO:トラック番号が異なる場合の対応方法**

### 対応するYoutube Musicのアルバムがない場合

 * `youtube_collection_name`
 * `youtube_track_name`
 * `youtube_collection_view_url`
 * `youtube_track_view_url`

をすべて「不明」にする。

例
```
collection_name	track_name	artist_name	track_number	release_date	apple_collection_view_url	apple_track_view_url	youtube_collection_name	youtube_track_name	youtube_collection_view_url	youtube_track_view_url
東方ホムーラン	Usa mimi mode	COOL&CREATE	2	2005-05-04 12:00:00 UTC	https://music.apple.com/jp/album/toho-homu-ran/1492786623?uo=4	https://music.apple.com/jp/album/usa-mimi-mode/1492786623?i=1492786625&uo=4	不明	不明	不明	不明
```

