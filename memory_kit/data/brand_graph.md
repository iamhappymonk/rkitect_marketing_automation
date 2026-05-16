# rkitect-marketing · brand graph

From mem0 Kuzu store at `/Users/b/.mem0/rkitect-marketing/kuzu.db`. 14 entities · 17 relationships.

## Entities by type

### Entity  (14)

- rkitect.ai
- 60_seconds
- alternative
- 3_hours
- client
- client_calls
- 9am
- presentation
- traditional_render_farm
- sketch
- render
- coffee
- architects
- 6-hour_render_nights

## Relationships by type

### CONNECTED_TO  (17)

- `rkitect.ai`  →  `60_seconds`
- `rkitect.ai`  →  `presentation`
- `rkitect.ai`  →  `rkitect.ai`
- `rkitect.ai`  →  `sketch`
- `60_seconds`  →  `3_hours`
- `alternative`  →  `3_hours`
- `client`  →  `client_calls`
- `client_calls`  →  `9am`
- `presentation`  →  `9am`
- `presentation`  →  `60_seconds`
- `traditional_render_farm`  →  `rkitect.ai`
- `sketch`  →  `render`
- `render`  →  `coffee`
- `render`  →  `architects`
- `render`  →  `6-hour_render_nights`
- `architects`  →  `6-hour_render_nights`
- `architects`  →  `render`
