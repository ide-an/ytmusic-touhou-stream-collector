grep -v "不明\s不明" result_patched_sorted.tsv >  archive/a.tsv
head -1 result_patched_sorted.tsv  >  archive/b.tsv
grep "不明\s不明" result_patched_sorted.tsv  >>  archive/b.tsv
