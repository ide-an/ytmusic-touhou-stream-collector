import sys
from pprint import pprint
from common import Seed, YTMusicResult, read_line, output_header, output_line

def sort_key(line):
    seed, result = read_line(line)
    return (seed.release_date, seed.collection_name, int(seed.track_number), seed.track_name)

def main(args):
    pprint(args)
    if len(args) < 3:
        print("[usage] python sort.py in_file out_file")
        sys.exit(1)
    in_file = args[1]
    out_file = args[2]
    lines = []
    with open(in_file,encoding="utf-8") as f_in:
        is_header = True
        for line in f_in:
            if is_header: # ヘッダ行skip
                is_header = False
                continue
            lines.append(line)
    lines = sorted(lines, key=sort_key)
    with open(out_file,"wt",encoding="utf-8") as f_out:
        output_header(f_out)
        for line in lines:
            f_out.write(line)


if __name__ == "__main__":
    main(sys.argv)
