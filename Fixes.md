

## 🔴 Critical Bugs (Core Logic is Broken)

<!-- ### 1. AI risk scores are silently ignored
This is the most important bug. `ai_utils.py` asks Claude for risk scores keyed by **zone name** (e.g. `"Downtown": 0.8`), but `graph_utils.py → update_edge_weights()` does lookups by **zone ID** (e.g. `"z1"`). The two never match — risk scores are effectively **always 0**, meaning the AI integration does nothing. -->

<!-- ### 2. `shortest_route` is always `null`
`routes.py` hardcodes `shortest_route=None`. The PRD's core selling point ("shortest ≠ safest comparison") is never shown. `RouteInfo.jsx` has the UI for it, it just has no data. -->

<!-- ### 3. `find_safest_path` is identical to `find_shortest_path`
There's no separate unweighted graph for comparison — both methods are literally the same function. -->

<!-- ### 4. Graph is a mutable singleton — corrupts on repeated calls
`city_graph = CityGraph()` is created once at module level. Every API call re-adds zones/roads to the same NetworkX graph, producing duplicate edges and corrupting weights. -->

---

## 🟡 Missing PRD Features

| Feature | Status |
|---|---|
| Interactive Leaflet map | ❌ `leaflet` is installed but never used — map is just CSS cards |
| Shortest vs. safest comparison | ❌ Always `null` |
| Zone coloring by danger level | ❌ No real map |
| A\* algorithm (PRD explicitly lists it) | ❌ Not implemented |
| Route drawn as polyline on map | ❌ No real map |

---

## 🟠 Other Issues

- Zone IDs (`z1`, `z3`) shown in UI instead of readable names
- API URL hardcoded in two places in `App.jsx` (should be a `VITE_API_URL` env var)
- Errors shown as `alert()` instead of a styled component
- No server-side validation that start/end zones actually exist (crashes as 500)
- `index.css` is still the Vite boilerplate template (unused variables like `--code-bg`, `--social-bg`)
- `anthropic==0.25.6` is very outdated (current: 0.49+)

---

## Priority Fix Order

1. **Fix zone name→ID mismatch** — makes AI actually work
2. **Implement `shortest_route`** — core PRD comparison feature  
3. **Replace `MapDisplay` with real Leaflet map** — biggest visual upgrade  
4. **Fix graph singleton** — data correctness  
5. **Add A\* algorithm** — explicitly in PRD  
6. **Show zone names instead of IDs** — UX polish  

Would you like me to start fixing these, one group at a time?