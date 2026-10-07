#!/bin/bash
# Usage: arcgis_layers.sh <outdir> <service>...
# Saves each FeatureServer's service JSON and each layer's JSON (fields, counts) to outdir.
base="https://services3.arcgis.com/XthfLqjm6BwtGUpE/arcgis/rest/services"
out="$1"; shift
mkdir -p "$out"
for s in "$@"; do
  curl -sS -m 60 "$base/$s/FeatureServer?f=json" -o "$out/${s}.json"
  ids=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(" ".join(str(l["id"]) for l in d.get("layers",[])+d.get("tables",[])))' "$out/${s}.json")
  for id in $ids; do
    curl -sS -m 60 "$base/$s/FeatureServer/$id?f=json" -o "$out/${s}_L${id}.json"
    cnt=$(curl -sS -m 60 "$base/$s/FeatureServer/$id/query?where=1%3D1&returnCountOnly=true&f=json")
    echo "$cnt" > "$out/${s}_L${id}_count.json"
  done
done
