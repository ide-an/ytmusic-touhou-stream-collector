import ytmusicapi
# patch.tsv作成時にアルバムURL探すのがめんどいのでcliで検索するツールを作る
def main():
    yt = ytmusicapi.YTMusic("header_auth.json", language="ja")
    print("""[usage]
    :s title\tinput title to search
    :q\tquit
    """)
    while True:
        print(">", end="")
        cmd = input().strip()
        if cmd == ":q":
            break
        elif cmd.startswith(":s "):
            results = yt.search(cmd[3:],"albums", limit=100) 
            for r in results:
                print("{} {} {}".format(r["title"], r["artist"], r["browseId"]))
        else:
            print("???")

if __name__ == "__main__":
    main()
