# ytmusic-touhou-stream-collector

## What's this?

ytmusic-touhou-stream-collectorは[東方同人音楽流通](https://touhou-music.jp/)経由でYoutube Musicにストリーム配信されている東方アレンジを収集するスクリプトです。

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
```
