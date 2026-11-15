#!/bin/sh
# Builds frontend/vendor/geolibre/ from the GeoLibre packages on npm. Needs Node 20+.
set -e
cd "$(dirname "$0")"
npm install --no-audit --no-fund
out=../app/static/geolibre
mkdir -p "$out"
npx esbuild entry.mjs --bundle --format=iife --global-name=GeoLibre --minify --loader:.wasm=dataurl --log-level=warning --outfile="$out/geolibre-map.js"
cp node_modules/maplibre-gl/dist/maplibre-gl.css node_modules/maplibre-gl/dist/maplibre-gl-worker.mjs node_modules/maplibre-gl/dist/maplibre-gl-shared.mjs "$out/"
cp node_modules/@geolibre/map/../../../../LICENSE "$out/" 2>/dev/null || true
