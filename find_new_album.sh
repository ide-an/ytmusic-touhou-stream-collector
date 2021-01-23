for url in `cut -f10 result2.tsv`;
do
  len=`fgrep "$url" archive/result.tsv | wc -l`
  echo "$url	$len"
done
