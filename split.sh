grep -v "不明\s不明" result.tsv >  a.tsv
head -1 result.tsv > b.tsv
grep "不明\s不明" result.tsv >>  b.tsv
