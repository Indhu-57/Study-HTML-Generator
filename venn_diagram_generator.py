"""
venn_diagram_generator.py
==========================

Generates every Venn diagram (SVG) used in the Venn-Euler Diagram study
material HTML file, and can automatically drop them back into an existing
copy of that file in the correct order.

GEOMETRY
--------
Circle radius (R) and rectangle size are chosen so the circles are always
fully CONTAINED inside the rectangle (the "universal set" box), with the
"U" tag and the A / B / C labels drawn just inside the rectangle's edges.

    R              = 1.1 cm   (circle radius)
    D              = 1.7 cm   (distance between adjacent circle centres)
    overlap        = 2R - D = 0.5 cm
    2-circle box   = 5.0 cm x 3.0 cm
    3-circle box   = 5.0 cm x ~4.67 cm (equilateral triangle layout,
                     same 0.5 cm pairwise overlap between every pair)

Each region of a 2-set or 3-set Venn diagram is named with a short code:

    2-circle regions : 'A_only', 'B_only', 'AB', 'outside'
    3-circle regions : 'A_only', 'B_only', 'C_only',
                        'AB', 'AC', 'BC'   (pairwise-only lens, excludes triple)
                        'ABC'              (all three)
                        'outside'

`two_circle(highlight, ...)` / `three_circle(highlight, ...)` take a list of
region codes to shade and return a ready-to-embed <svg>...</svg> string
(sized in real cm via width/height attributes, so it always prints small).

USAGE
-----
    python venn_diagram_generator.py                  # writes sample SVGs to ./svg_out
    python venn_diagram_generator.py --apply FILE.html # regenerates every
                                                          diagram inside FILE.html,
                                                          in document order, and
                                                          overwrites it in place
"""

import re
import sys
import os
import argparse

# ----------------------------------------------------------------------
# 1. Low-level SVG building blocks
# ----------------------------------------------------------------------

_uid_counter = [0]


def _next_id(prefix):
    """Generate a short, guaranteed-unique id for a <mask>/<clipPath>."""
    _uid_counter[0] += 1
    return f"{prefix}{_uid_counter[0]}"


FILL = "#93c5fd"          # shaded-region fill colour
STROKE = "#0f2447"         # circle outline colour
RECT_STROKE = "#64748b"    # universal-set rectangle colour
LABEL_COL = "#0f2447"      # A / B / C label colour

R = 1.1            # circle radius (cm)
D = 1.7            # distance between adjacent circle centres (cm) -> 0.5cm overlap
SIDE_MARGIN = 0.55  # horizontal margin between a circle and the rectangle edge
TOP_LABEL = 0.5     # vertical space reserved at the top for A / B labels
PAD = 0.35          # padding between the rectangle and the SVG canvas edge


def _circle(cx, cy, r, extra=""):
    return f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" {extra}/>'


def _wrap(canvas_w, canvas_h, body, defs):
    """Wrap the drawn body in an <svg> sized in real centimetres."""
    return (
        f'<svg viewBox="0 0 {canvas_w:.3f} {canvas_h:.3f}" '
        f'width="{canvas_w:.2f}cm" height="{canvas_h:.2f}cm" '
        f'xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">'
        f"<defs>{defs}</defs>{body}</svg>"
    )


# ----------------------------------------------------------------------
# 2. Two-circle Venn diagram
# ----------------------------------------------------------------------

def two_circle(highlight, label_a="A", label_b="B"):
    """
    highlight: subset of {'A_only', 'B_only', 'AB', 'outside'}
    Returns an <svg> string. Circles are guaranteed to sit fully inside
    the 5cm x 3cm rectangle.
    """
    rect_w = D + 2 * R + 2 * SIDE_MARGIN     # 5.0 cm
    rect_h = 3.0                              # cm
    canvas_w, canvas_h = rect_w + 2 * PAD, rect_h + 2 * PAD
    rx, ry = PAD, PAD

    Ax, Ay = rx + SIDE_MARGIN + R, ry + TOP_LABEL + R
    Bx, By = Ax + D, Ay

    m_a, m_b, m_out, clip_ab = (_next_id("m"), _next_id("m"),
                                 _next_id("m"), _next_id("c"))
    defs = (
        f'<mask id="{m_a}"><rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" '
        f'fill="white"/>{_circle(Bx, By, R, 'fill="black"')}</mask>'
        f'<mask id="{m_b}"><rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" '
        f'fill="white"/>{_circle(Ax, Ay, R, 'fill="black"')}</mask>'
        f'<mask id="{m_out}"><rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" '
        f'fill="white"/>{_circle(Ax, Ay, R, 'fill="black"')}'
        f'{_circle(Bx, By, R, 'fill="black"')}</mask>'
        f'<clipPath id="{clip_ab}">{_circle(Bx, By, R)}</clipPath>'
    )

    body = (
        f'<rect x="{rx}" y="{ry}" width="{rect_w:.3f}" height="{rect_h:.3f}" '
        f'fill="none" stroke="{RECT_STROKE}" stroke-width="0.045" rx="0.1"/>'
    )
    body += (
        f'<text x="{rx+0.13:.3f}" y="{ry+0.32:.3f}" font-size="0.3" '
        f'fill="{RECT_STROKE}" font-family="Inter, sans-serif" font-weight="600">U</text>'
    )

    if "A_only" in highlight:
        body += f'<g opacity="0.75"><g mask="url(#{m_a})">{_circle(Ax, Ay, R, f'fill="{FILL}"')}</g></g>'
    if "B_only" in highlight:
        body += f'<g opacity="0.75"><g mask="url(#{m_b})">{_circle(Bx, By, R, f'fill="{FILL}"')}</g></g>'
    if "AB" in highlight:
        body += f'<g opacity="0.75"><g clip-path="url(#{clip_ab})">{_circle(Ax, Ay, R, f'fill="{FILL}"')}</g></g>'
    if "outside" in highlight:
        body += (
            f'<g opacity="0.75"><g mask="url(#{m_out})">'
            f'<rect x="{rx}" y="{ry}" width="{rect_w:.3f}" height="{rect_h:.3f}" '
            f'fill="{FILL}"/></g></g>'
        )

    body += _circle(Ax, Ay, R, f'fill="none" stroke="{STROKE}" stroke-width="0.05"')
    body += _circle(Bx, By, R, f'fill="none" stroke="{STROKE}" stroke-width="0.05"')
    body += (
        f'<text x="{Ax:.3f}" y="{ry+0.34:.3f}" text-anchor="middle" font-size="0.32" '
        f'font-weight="700" fill="{LABEL_COL}" font-family="Merriweather, serif">{label_a}</text>'
    )
    body += (
        f'<text x="{Bx:.3f}" y="{ry+0.34:.3f}" text-anchor="middle" font-size="0.32" '
        f'font-weight="700" fill="{LABEL_COL}" font-family="Merriweather, serif">{label_b}</text>'
    )
    return _wrap(canvas_w, canvas_h, body, defs)


# ----------------------------------------------------------------------
# 3. Three-circle Venn diagram
# ----------------------------------------------------------------------

def three_circle(highlight, label_a="A", label_b="B", label_c="C"):
    """
    highlight: subset of {'A_only','B_only','C_only','AB','AC','BC','ABC','outside'}
    ('AB' / 'AC' / 'BC' are the pairwise-only lens, excluding the centre.)
    Equilateral-triangle layout so every pair of circles overlaps by the
    same 0.5cm amount. Circles are guaranteed to sit fully inside the box.
    """
    h = D * (3 ** 0.5) / 2
    rect_w = D + 2 * R + 2 * SIDE_MARGIN      # 5.0 cm
    bottom_label = 0.5                         # space reserved for the C label
    rect_h = TOP_LABEL + h + 2 * R + bottom_label
    canvas_w, canvas_h = rect_w + 2 * PAD, rect_h + 2 * PAD
    rx, ry = PAD, PAD

    Ax, Ay = rx + SIDE_MARGIN + R, ry + TOP_LABEL + R
    Bx, By = Ax + D, Ay
    Cx, Cy = (Ax + Bx) / 2, Ay + h

    m_a, m_b, m_c, m_out = (_next_id("m"), _next_id("m"), _next_id("m"), _next_id("m"))
    c_a, c_b, c_c = _next_id("c"), _next_id("c"), _next_id("c")

    defs = (
        f'<mask id="{m_a}"><rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" fill="white"/>'
        f'{_circle(Bx, By, R, 'fill="black"')}{_circle(Cx, Cy, R, 'fill="black"')}</mask>'
        f'<mask id="{m_b}"><rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" fill="white"/>'
        f'{_circle(Ax, Ay, R, 'fill="black"')}{_circle(Cx, Cy, R, 'fill="black"')}</mask>'
        f'<mask id="{m_c}"><rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" fill="white"/>'
        f'{_circle(Ax, Ay, R, 'fill="black"')}{_circle(Bx, By, R, 'fill="black"')}</mask>'
        f'<mask id="{m_out}"><rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" fill="white"/>'
        f'{_circle(Ax, Ay, R, 'fill="black"')}{_circle(Bx, By, R, 'fill="black"')}'
        f'{_circle(Cx, Cy, R, 'fill="black"')}</mask>'
        f'<clipPath id="{c_a}">{_circle(Ax, Ay, R)}</clipPath>'
        f'<clipPath id="{c_b}">{_circle(Bx, By, R)}</clipPath>'
        f'<clipPath id="{c_c}">{_circle(Cx, Cy, R)}</clipPath>'
    )

    body = (
        f'<rect x="{rx}" y="{ry}" width="{rect_w:.3f}" height="{rect_h:.3f}" '
        f'fill="none" stroke="{RECT_STROKE}" stroke-width="0.045" rx="0.1"/>'
    )
    body += (
        f'<text x="{rx+0.13:.3f}" y="{ry+0.32:.3f}" font-size="0.3" '
        f'fill="{RECT_STROKE}" font-family="Inter, sans-serif" font-weight="600">U</text>'
    )

    def region(mask_id, circle_svg):
        return f'<g opacity="0.75"><g mask="url(#{mask_id})">{circle_svg}</g></g>'

    if "A_only" in highlight:
        body += region(m_a, _circle(Ax, Ay, R, f'fill="{FILL}"'))
    if "B_only" in highlight:
        body += region(m_b, _circle(Bx, By, R, f'fill="{FILL}"'))
    if "C_only" in highlight:
        body += region(m_c, _circle(Cx, Cy, R, f'fill="{FILL}"'))
    if "AB" in highlight:
        body += (f'<g opacity="0.75"><g mask="url(#{m_c})"><g clip-path="url(#{c_b})">'
                  f'{_circle(Ax, Ay, R, f'fill="{FILL}"')}</g></g></g>')
    if "AC" in highlight:
        body += (f'<g opacity="0.75"><g mask="url(#{m_b})"><g clip-path="url(#{c_c})">'
                  f'{_circle(Ax, Ay, R, f'fill="{FILL}"')}</g></g></g>')
    if "BC" in highlight:
        body += (f'<g opacity="0.75"><g mask="url(#{m_a})"><g clip-path="url(#{c_c})">'
                  f'{_circle(Bx, By, R, f'fill="{FILL}"')}</g></g></g>')
    if "ABC" in highlight:
        body += (f'<g opacity="0.75"><g clip-path="url(#{c_b})"><g clip-path="url(#{c_c})">'
                  f'{_circle(Ax, Ay, R, f'fill="{FILL}"')}</g></g></g>')
    if "outside" in highlight:
        body += region(m_out, f'<rect x="{rx}" y="{ry}" width="{rect_w:.3f}" height="{rect_h:.3f}" fill="{FILL}"/>')

    for cx, cy in [(Ax, Ay), (Bx, By), (Cx, Cy)]:
        body += _circle(cx, cy, R, f'fill="none" stroke="{STROKE}" stroke-width="0.05"')

    body += (f'<text x="{Ax:.3f}" y="{ry+0.34:.3f}" text-anchor="middle" font-size="0.32" '
              f'font-weight="700" fill="{LABEL_COL}" font-family="Merriweather, serif">{label_a}</text>')
    body += (f'<text x="{Bx:.3f}" y="{ry+0.34:.3f}" text-anchor="middle" font-size="0.32" '
              f'font-weight="700" fill="{LABEL_COL}" font-family="Merriweather, serif">{label_b}</text>')
    body += (f'<text x="{Cx:.3f}" y="{ry+rect_h-0.14:.3f}" text-anchor="middle" font-size="0.32" '
              f'font-weight="700" fill="{LABEL_COL}" font-family="Merriweather, serif">{label_c}</text>')

    return _wrap(canvas_w, canvas_h, body, defs)


# ----------------------------------------------------------------------
# 4. The full 35-diagram plan used in the study-material HTML
#    (order must match the order the <svg> tags appear in the document)
# ----------------------------------------------------------------------

PLAN = [
    # --- Definitions page (6 diagrams) ---
    ("2", [], "A", "B"),                                        # outline only
    ("2", ["A_only", "B_only", "AB", "outside"], "A", "B"),      # Universal Set U
    ("2", ["A_only", "B_only", "AB"], "A", "B"),                 # Union A U B
    ("2", ["AB"], "A", "B"),                                     # Intersection A ∩ B
    ("2", ["A_only"], "A", "B"),                                 # Set difference A - B
    ("2", ["B_only", "outside"], "A", "B"),                      # Complement A'

    # --- Example 1: A U (B ∩ C) = (A U B) ∩ (A U C) ---
    ("3", ["BC", "ABC"], "A", "B", "C"),                                        # LHS step 1
    ("3", ["A_only", "AB", "AC", "ABC"], "A", "B", "C"),                        # LHS step 2
    ("3", ["A_only", "AB", "AC", "ABC", "BC"], "A", "B", "C"),                  # LHS step 3
    ("3", ["A_only", "B_only", "AB", "AC", "BC", "ABC"], "A", "B", "C"),        # RHS step 1
    ("3", ["A_only", "C_only", "AB", "AC", "BC", "ABC"], "A", "B", "C"),        # RHS step 2
    ("3", ["A_only", "AB", "AC", "BC", "ABC"], "A", "B", "C"),                  # RHS step 3

    # --- Example 2: A ∩ (B U C) = (A ∩ B) U (A ∩ C) ---
    ("3", ["B_only", "C_only", "AB", "AC", "BC", "ABC"], "A", "B", "C"),        # LHS step 1
    ("3", ["A_only", "AB", "AC", "ABC"], "A", "B", "C"),                        # LHS step 2
    ("3", ["AB", "AC", "ABC"], "A", "B", "C"),                                  # LHS step 3
    ("3", ["AB", "ABC"], "A", "B", "C"),                                        # RHS step 1
    ("3", ["AC", "ABC"], "A", "B", "C"),                                        # RHS step 2
    ("3", ["AB", "AC", "ABC"], "A", "B", "C"),                                  # RHS step 3

    # --- Example 3: (A U B)' = A' ∩ B' ---
    ("2", ["A_only", "B_only", "AB"], "A", "B"),                # LHS step 1
    ("2", ["outside"], "A", "B"),                                # LHS step 2
    ("2", ["B_only", "outside"], "A", "B"),                      # RHS step 1
    ("2", ["A_only", "outside"], "A", "B"),                      # RHS step 2
    ("2", ["outside"], "A", "B"),                                # RHS step 3

    # --- Example 4: (A ∩ B)' = A' U B' ---
    ("2", ["AB"], "A", "B"),                                     # LHS step 1
    ("2", ["A_only", "B_only", "outside"], "A", "B"),            # LHS step 2
    ("2", ["B_only", "outside"], "A", "B"),                      # RHS step 1
    ("2", ["A_only", "outside"], "A", "B"),                      # RHS step 2
    ("2", ["A_only", "B_only", "outside"], "A", "B"),            # RHS step 3

    # --- Example 5: A' - B' = B - A ---
    ("2", ["B_only", "outside"], "A", "B"),                      # LHS step 1
    ("2", ["A_only", "outside"], "A", "B"),                      # LHS step 2
    ("2", ["B_only"], "A", "B"),                                 # LHS step 3
    ("2", ["B_only", "AB"], "A", "B"),                           # RHS step 1
    ("2", ["B_only"], "A", "B"),                                 # RHS step 2

    # --- Inclusion-Exclusion derivation ---
    ("2", ["A_only", "B_only", "AB"], "A", "B"),

    # --- Practice Problem 2: shade A' U B ---
    ("2", ["B_only", "AB", "outside"], "A", "B"),
]


def build_all_svgs(plan=PLAN):
    """Return the list of <svg> strings for the given plan, in order."""
    svgs = []
    for spec in plan:
        if spec[0] == "2":
            _, highlight, la, lb = spec
            svgs.append(two_circle(highlight, la, lb))
        else:
            _, highlight, la, lb, lc = spec
            svgs.append(three_circle(highlight, la, lb, lc))
    return svgs


# ----------------------------------------------------------------------
# 5. Optional: patch an existing HTML file in place
# ----------------------------------------------------------------------

def apply_to_html(path):
    """Replace every <svg>...</svg> block in `path`, in document order,
    with a freshly generated diagram from PLAN. The file is overwritten."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    existing = re.findall(r"<svg.*?</svg>", content, re.S)
    if len(existing) != len(PLAN):
        raise ValueError(
            f"Found {len(existing)} <svg> blocks but PLAN has {len(PLAN)} entries. "
            "Update PLAN to match the document before applying."
        )

    new_svgs = iter(build_all_svgs())
    content = re.sub(r"<svg.*?</svg>", lambda m: next(new_svgs), content, flags=re.S)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Replaced {len(existing)} diagrams in {path}")


# ----------------------------------------------------------------------
# 6. CLI
# ----------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", metavar="FILE.html",
                         help="Regenerate every diagram inside this HTML file, in place.")
    parser.add_argument("--out", default="svg_out",
                         help="Directory to write sample SVG files to (default: ./svg_out)")
    args = parser.parse_args()

    if args.apply:
        apply_to_html(args.apply)
    else:
        os.makedirs(args.out, exist_ok=True)
        svgs = build_all_svgs()
        for i, svg in enumerate(svgs):
            with open(os.path.join(args.out, f"diagram_{i:02d}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
        print(f"Wrote {len(svgs)} sample diagrams to ./{args.out}/")
        print("Tip: run with --apply path/to/Venn-Euler_Diagram_Study_Material.html "
              "to regenerate all diagrams inside that file in place.")
