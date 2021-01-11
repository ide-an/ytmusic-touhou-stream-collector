# ytmusic-touhou-stream-collector

## What's this?

ytmusic-touhou-stream-collectorは[東方同人音楽流通](https://touhou-music.jp/)経由でYoutube Musicにストリーム配信されている東方アレンジを収集するスクリプトです。

リストのシードデータとして @shiroemons氏による[AppleMusicの配信リスト](https://docs.google.com/spreadsheets/d/1h1M6Q0UPGvF8kTIiw0F5c7k0mGlkyhrI4kSkASRV_bw)を利用しています。

## How to run

### Set up

https://ytmusicapi.readthedocs.io/en/latest/setup.html#authenticated-requests を参考に`header_auth.json`を作成する。

### Run with Docker

*TODO:書く*
```sh
docker build -t ytmusic-touhou-stream-collector .
docker run --rm ytmusic-touhou-stream-collector
```
