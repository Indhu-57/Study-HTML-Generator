"""
Generates real, geometrically correct SVG Venn diagrams for 2 or 3 sets.

This does NOT need an image-generation model — Venn diagram geometry is
fixed and well known (2 or 3 overlapping circles), so we can draw it
directly as SVG based on a small JSON spec Gemini produces, e.g.:

    {
      "type": "venn2",
      "labels": ["A", "B"],
      "shaded": ["A_and_B"],
      "values": {"A_only": 12, "B_only": 8, "A_and_B": 5}
    }

Supported region keys:
  venn2: A_only, B_only, A_and_B, outside
  venn3: A_only, B_only, C_only, A_and_B_only, A_and_C_only,
         B_and_C_only, A_and_B_and_C, outside
"""

_SHADE_COLOR = "#93c5fd"
_SHADE_OPACITY = "0.75"

_VENN2_GEOMETRY = {
    "A": (150, 140, 95),
    "B": (250, 140, 95),
}

_VENN3_GEOMETRY = {
    "A": (150, 120, 85),
    "B": (230, 120, 85),
    "C": (190, 190, 85),
}


def _uid(prefix, idx):
    return f"{prefix}{idx}"


def _rect(idx):
    return f'<rect id="{_uid("uni", idx)}" x="10" y="10" width="380" height="260" fill="white" stroke="none"/>'


def _circle_tag(cx, cy, r, id_):
    return f'<circle id="{id_}" cx="{cx}" cy="{cy}" r="{r}"/>'


def _build_region_element(idx, include, exclude, geometry, fill, universe_wh):
    """
    Builds an SVG element (chained clip-paths for intersections, a mask for
    subtractions) representing the region that is inside every circle in
    `include` and outside every circle in `exclude`.
    Returns (defs_snippet, element_snippet).
    """
    defs = []
    w, h = universe_wh

    mask_id = None
    if exclude:
        mask_id = _uid(f"mask_{idx}_", "_".join(exclude))
        mask_children = f'<rect x="0" y="0" width="{w}" height="{h}" fill="white"/>'
        for name in exclude:
            cx, cy, r = geometry[name]
            mask_children += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="black"/>'
        defs.append(f'<mask id="{mask_id}">{mask_children}</mask>')

    if include:
        base_name = include[0]
        cx, cy, r = geometry[base_name]
        base_shape = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
    else:
        # "outside" region for a 3-set diagram with no includes: whole universe
        base_shape = f'<rect x="10" y="10" width="{w-20}" height="{h-20}" fill="{fill}"/>'

    # Wrap in nested clip-path groups for every additional included circle
    # (nested clip-paths intersect).
    element = base_shape
    for name in include[1:]:
        cx, cy, r = geometry[name]
        clip_id = _uid(f"clip_{idx}_", name)
        defs.append(f'<clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
        element = f'<g clip-path="url(#{clip_id})">{element}</g>'

    if mask_id:
        element = f'<g mask="url(#{mask_id})">{element}</g>'

    return "".join(defs), element


def _label_position(region, geometry, kind):
    if kind == "venn2":
        ax, ay, ar = geometry["A"]
        bx, by, br = geometry["B"]
        positions = {
            "A_only": (ax - 35, ay),
            "B_only": (bx + 35, ay),
            "A_and_B": ((ax + bx) / 2, ay),
            "outside": (200, 30),
        }
    else:
        ax, ay, ar = geometry["A"]
        bx, by, br = geometry["B"]
        cx, cy, cr = geometry["C"]
        positions = {
            "A_only": (ax - 40, ay - 20),
            "B_only": (bx + 40, by - 20),
            "C_only": (cx, cy + 55),
            "A_and_B_only": ((ax + bx) / 2, ay - 35),
            "A_and_C_only": ((ax + cx) / 2 - 15, (ay + cy) / 2 + 15),
            "B_and_C_only": ((bx + cx) / 2 + 15, (by + cy) / 2 + 15),
            "A_and_B_and_C": ((ax + bx + cx) / 3, (ay + by + cy) / 3),
            "outside": (200, 25),
        }
    return positions.get(region, (200, 150))


_VENN2_REGION_DEF = {
    "A_only": (["A"], ["B"]),
    "B_only": (["B"], ["A"]),
    "A_and_B": (["A", "B"], []),
    "outside": ([], ["A", "B"]),
}

_VENN3_REGION_DEF = {
    "A_only": (["A"], ["B", "C"]),
    "B_only": (["B"], ["A", "C"]),
    "C_only": (["C"], ["A", "B"]),
    "A_and_B_only": (["A", "B"], ["C"]),
    "A_and_C_only": (["A", "C"], ["B"]),
    "B_and_C_only": (["B", "C"], ["A"]),
    "A_and_B_and_C": (["A", "B", "C"], []),
    "outside": ([], ["A", "B", "C"]),
}


def _render(kind, labels, shaded, values, idx=0):
    if kind == "venn2":
        geometry_keys = ["A", "B"]
        geometry = {k: _VENN2_GEOMETRY[k] for k in geometry_keys}
        region_defs = _VENN2_REGION_DEF
    else:
        geometry_keys = ["A", "B", "C"]
        geometry = {k: _VENN3_GEOMETRY[k] for k in geometry_keys}
        region_defs = _VENN3_REGION_DEF

    universe_wh = (400, 280)
    defs_parts = []
    shade_elements = []

    for region in shaded or []:
        if region not in region_defs:
            continue
        include, exclude = region_defs[region]
        d, el = _build_region_element(f"{idx}_{region}", include, exclude, geometry, _SHADE_COLOR, universe_wh)
        defs_parts.append(d)
        shade_elements.append(f'<g opacity="{_SHADE_OPACITY}">{el}</g>')

    # Circle outlines + labels
    outline_elements = []
    for i, key in enumerate(geometry_keys):
        cx, cy, r = geometry[key]
        outline_elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0f2447" stroke-width="2.5"/>')

    label_positions_outside = {
        "A": (geometry["A"][0] - geometry["A"][2] * 0.75, geometry["A"][1] - geometry["A"][2] - 6) if kind == "venn2"
             else (geometry["A"][0] - geometry["A"][2] * 0.9, geometry["A"][1] - geometry["A"][2] * 0.6),
        "B": (geometry["B"][0] + geometry["B"][2] * 0.55, geometry["B"][1] - geometry["B"][2] - 6) if kind == "venn2"
             else (geometry["B"][0] + geometry["B"][2] * 0.7, geometry["B"][1] - geometry["B"][2] * 0.6),
    }
    if kind == "venn3":
        label_positions_outside["C"] = (geometry["C"][0], geometry["C"][1] + geometry["C"][2] + 20)

    set_labels = {}
    for i, key in enumerate(geometry_keys):
        name = labels[i] if i < len(labels) else key
        set_labels[key] = name

    label_elements = []
    for key in geometry_keys:
        lx, ly = label_positions_outside[key]
        label_elements.append(
            f'<text x="{lx}" y="{ly}" font-size="18" font-weight="700" fill="#0f2447" font-family="Merriweather, serif">{set_labels[key]}</text>'
        )

    # Value numbers inside regions (only for regions the caller provided a value for)
    value_elements = []
    for region, val in (values or {}).items():
        if region not in region_defs:
            continue
        vx, vy = _label_position(region, geometry, kind)
        value_elements.append(
            f'<text x="{vx}" y="{vy}" font-size="15" font-weight="600" fill="#1e293b" text-anchor="middle" font-family="Inter, sans-serif">{val}</text>'
        )

    svg = f'''<svg viewBox="0 0 400 280" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">
<defs>{"".join(defs_parts)}</defs>
<rect x="10" y="10" width="380" height="260" fill="none" stroke="#64748b" stroke-width="1.5" rx="6"/>
<text x="20" y="30" font-size="13" fill="#64748b" font-family="Inter, sans-serif">U</text>
{"".join(shade_elements)}
{"".join(outline_elements)}
{"".join(label_elements)}
{"".join(value_elements)}
</svg>'''
    return svg


def render_venn_svg(spec, idx=0):
    """
    spec: dict like {"type": "venn2"|"venn3", "labels": [...], "shaded": [...], "values": {...}}
    idx: unique index so multiple diagrams on one page don't clash on SVG ids.
    Returns an SVG string, or None if the spec is missing/invalid.
    """
    if not isinstance(spec, dict):
        return None
    kind = spec.get("type")
    if kind not in ("venn2", "venn3"):
        return None

    labels = spec.get("labels") or (["A", "B"] if kind == "venn2" else ["A", "B", "C"])
    shaded = spec.get("shaded") or []
    values = spec.get("values") or {}

    try:
        return _render(kind, labels, shaded, values, idx=idx)
    except Exception:
        return None
