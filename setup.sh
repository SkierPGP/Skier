#!/usr/bin/env bash

echo "Converting markdown into HTML..."

for f in markdown/*.md; do
    name=${f##*/}
    echo "$f -> templates/generated/${name%.md}.html"
    pandoc -f markdown -t html -o templates/generated/${name%.md}.html ${f}
done
