# ReadingLadder — Component Cut List

Derived from the **nominal design spec** (not the as-built massing solid, which
carries a +¾" shell artifact). All dimensions in inches.

## Construction assumptions

- **Sheet parts:** ¾" plywood. **Linear parts:** solid lumber.
- **Joinery:** butt joints throughout (glue + fasteners/pocket screws).
- The two **side panels are the outer skin**; every other panel runs **22.5"**
  between them (24 overall − 2 × ¾").
- Dimensions are *face* dimensions. Where two ¾" parts meet, absorb the overlap
  into your chosen joint (dado/rabbet/butt) — figures below assume simple butt.
- Overall assembled envelope: **42" deep × 24" wide × 46" high** (grab post
  extends to **60"**).

## Side-profile polygon (for the side panels)

Cut each side to this outline (X = depth from back, Z = height), inches:

```
(0,0) (0,8) (10,8) (10,16) (20,16) (20,24) (30,24) (30,46) (42,42) (42,0)
```

## Plywood parts (¾")

| ID | Part | Qty | L × W (in) | Notes |
|----|------|----:|-----------|-------|
| A  | Side panel | 2 | 42 × 46 (profile) | Cut to side-profile polygon above. **LEFT** panel only: cut an 18.5 × 14.5 side-shelf opening, located 10.75" from back edge, 0.75" up from bottom. Grain runs vertical. |
| B  | Step tread | 3 | 22.5 × 10 | Horizontal; treads at z = 8, 16, 24 (top = platform). |
| C  | Riser | 3 | 22.5 × 8 | Vertical; risers at x = 0, 10, 20. |
| D  | Lectern back wall | 1 | 22.5 × 22 | Vertical at x = 30, z 24→46; separates platform from lectern. |
| E  | Lectern front | 1 | 22.5 × 42 | Vertical at x = 42. Cut **three cubby openings**, each 21" wide (¾" frame each side): C1 z 0→13, C2 z 13.75→26.5, C3 z 27.25→40. |
| F  | Reading surface | 1 | 22.5 × 12&nbsp;5⁄8 | Sloped top (≈18.4°). Bevel both long edges ≈18° to seat on the lectern-back top (z 46) and meet the front lip. |
| G  | Cubby shelf | 2 | 22.5 × 10.5 | Horizontal dividers inside the cubby, at z = 13 and z = 26.5. Depth = cubby depth. |
| H  | Cubby back *(optional)* | 1 | 22.5 × 40 | Vertical at x = 31.5; boxes the cubby off from the lower carcass. Omit to leave cubby open to the case interior. |
| J  | Bottom panel *(optional)* | 1 | 22.5 × 42 | Closes the underside (the model leaves it open; add for a finished base/dust seal). |

## Lumber parts

| ID | Part | Qty | Section × Length (in) | Notes |
|----|------|----:|-----------------------|-------|
| K  | Grab post | 1 | 1.5 × 1.5 × 36 | A 2×2 (dresses to 1.5" sq). Mounts at left-front of platform (x≈21, z 24→60); through-tenon or bracket into platform. |
| L  | Front lip | 1 | ¾ × 1.5 × 22.5 | Rail along the front edge of the reading surface; book stop. Can be a plywood rip if preferred. |

## Sheet-goods estimate (¾" ply, 4×8 sheets = 48 × 96")

| Scope | Parts | ≈ Sheets |
|-------|-------|---------:|
| Core (A–G) | 2 sides, 3 treads, 3 risers, lectern front/back, reading surface, 2 shelves | **≈ 2–3** |
| + Optional (H, J) | cubby back, bottom | **+1** |

Two sides dominate the yield (each ~42 × 46). Nest the small parts (treads,
risers, shelves) into the offcuts around the side profiles.

## Lumber estimate

- One **8' 2×2** covers the grab post (K) with margin.
- Front lip (L) from a 2' offcut of lumber or a ¾" ply rip.

## Not itemized

Fasteners, glue, cleats/glue-blocks, finish, and edge-banding for exposed
plywood edges — add per your build method.
