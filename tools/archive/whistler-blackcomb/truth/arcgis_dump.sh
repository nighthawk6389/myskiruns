#!/bin/bash
# Usage: arcgis_dump.sh <outdir> <service>/<layerId>...
# Downloads all features (all fields, WGS84 geometry) of each layer as GeoJSON, paging by 1000.
base="https://services3.arcgis.com/XthfLqjm6BwtGUpE/arcgis/rest/services"
out="$1"; shift
mkdir -p "$out"
for sl in "$@"; do
  s="${sl%%/*}"; rest="${sl#*/}"; id="${rest%%/*}"; oid="${rest#*/}"; [ "$oid" = "$rest" ] && oid=FID
  off=0; part=0
  while :; do
    fn="$out/${s}_L${id}_p${part}.geojson"
    curl -sS -m 120 -G "$base/$s/FeatureServer/$id/query" \
      --data-urlencode "where=1=1" --data-urlencode "outFields=*" \
      --data-urlencode "returnGeometry=true" --data-urlencode "outSR=4326" \
      --data-urlencode "orderByFields=$oid ASC" \
      --data-urlencode "resultOffset=$off" --data-urlencode "resultRecordCount=1000" \
      --data-urlencode "f=geojson" -o "$fn"
    n=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(len(d.get("features",[])) if "features" in d else -1)' "$fn")
    echo "$sl part=$part offset=$off features=$n"
    case "$n" in (""|-1) echo "  error reply, stopping"; break;; esac
    if [ "$n" -lt 1000 ]; then break; fi
    off=$((off+1000)); part=$((part+1))
  done
done
