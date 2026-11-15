// Browser bundle of GeoLibre's headless map layer (opengeos/GeoLibre, MIT) + MapLibre GL JS.
// Exposes window.GeoLibre. Rebuild with: sh geolibre/build.sh
import * as maplibregl from "maplibre-gl";
import { createLayerSync } from "@geolibre/map/headless";
import { DEFAULT_LAYER_STYLE } from "@geolibre/core";

/** A GeoLibre vector layer from a GeoJSON FeatureCollection. */
export function vectorLayer(id, name, fc, style = {}, extra = {}) {
  return { id, name, type: "geojson", source: {}, visible: true, opacity: 1,
           style: { ...DEFAULT_LAYER_STYLE, ...style }, metadata: {}, geojson: fc, ...extra };
}
/** Style fields for a rule-based renderer: colour by the value of one property. */
export function colourBy(prop, mapping, fallback = "#888888") {
  const rules = Object.entries(mapping).map(([v, color], i) =>
    ({ id: `r${i}`, label: v, filter: JSON.stringify(["==", ["get", prop], v]), color, isElse: false }));
  rules.push({ id: "else", label: "Other", filter: "", color: fallback, isElse: true });
  return { vectorStyleMode: "rule-based", vectorRules: rules };
}
export { maplibregl, createLayerSync, DEFAULT_LAYER_STYLE };
