#!/usr/bin/env bash

cd $1

echo "Converting markdown into HTML..."

for f in markdown/*.md; do
    name=${f##*/}
    echo "$f -> templates/generated/${name%.md}.html"
    pandoc -f markdown -t html -o templates/generated/${name%.md}.html ${f} --parse-raw
    echo "Fixing tags in templates/generated/${name%.md}.html"
    python3 tools/fix_md.py "templates/generated/${name%.md}.html"
done

echo "Generating server list.."
python3 tools/gen_server_list.py
