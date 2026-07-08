"""
Generates chart specs for the ILM Generator: bar charts, line charts, pie
charts, and function graphs (parabolas, sine/cosine waves, any y = f(x)).

Unlike Venn diagrams (rendered as static SVG), these are rendered in the
browser using Chart.js, since that's the simplest reliable way to draw
axes, gridlines, and smooth curves. html_generator.py embeds a <canvas>
placeholder plus a JSON config; script.js instantiates the actual charts
on page load.

Function graphs are evaluated SERVER-SIDE (here, in Python) using a
restricted AST-walking evaluator — not by eval()'ing Gemini's expression
string in the browser — so a malformed or unexpected expression can only
ever produce numbers or raise an error, never execute arbitrary code.
"""

import ast
import math

_ALLOWED_FUNCS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "exp": math.exp, "abs": abs,
}
_ALLOWED_CONSTS = {"pi": math.pi, "e": math.e}


class _UnsafeExpression(Exception):
    pass


def _safe_eval_node(node, x_value):
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body, x_value)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise _UnsafeExpression("Only numeric constants are allowed.")
    if isinstance(node, ast.Name):
        if node.id == "x":
            return x_value
        if node.id in _ALLOWED_CONSTS:
            return _ALLOWED_CONSTS[node.id]
        raise _UnsafeExpression(f"Unknown name: {node.id}")
    if isinstance(node, ast.BinOp):
        left = _safe_eval_node(node.left, x_value)
        right = _safe_eval_node(node.right, x_value)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        if isinstance(node.op, ast.Mod):
            return left % right
        raise _UnsafeExpression("Unsupported operator.")
    if isinstance(node, ast.UnaryOp):
        val = _safe_eval_node(node.operand, x_value)
        if isinstance(node.op, ast.USub):
            return -val
        if isinstance(node.op, ast.UAdd):
            return val
        raise _UnsafeExpression("Unsupported unary operator.")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            raise _UnsafeExpression("Only sin/cos/tan/sqrt/log/log10/exp/abs are allowed.")
        args = [_safe_eval_node(a, x_value) for a in node.args]
        return _ALLOWED_FUNCS[node.func.id](*args)
    raise _UnsafeExpression(f"Unsupported expression element: {type(node).__name__}")


def safe_eval_expr(expression, x_value):
    """
    Safely evaluates a single-variable math expression like "x^2 - 4" or
    "2*sin(3*x)" at a given x. Supports + - * / ^ % and
    sin/cos/tan/sqrt/log/log10/exp/abs, plus the constants pi and e.
    Raises _UnsafeExpression or a normal math error (e.g. ZeroDivisionError)
    on invalid input, which the caller should catch.
    """
    # Users/LLMs often write ^ for power; Python's AST uses ** for that.
    py_expr = expression.replace("^", "**")
    tree = ast.parse(py_expr, mode="eval")
    return _safe_eval_node(tree, x_value)


def compute_function_points(expression, x_min, x_max, steps=120):
    """
    Returns a list of {"x": ..., "y": ...} points for a function graph,
    skipping any x where evaluation fails (e.g. tan's asymptotes) rather
    than crashing the whole diagram.
    """
    points = []
    if steps < 2:
        steps = 2
    step_size = (x_max - x_min) / (steps - 1)
    for i in range(steps):
        x_val = x_min + i * step_size
        try:
            y_val = safe_eval_expr(expression, x_val)
            if isinstance(y_val, (int, float)) and math.isfinite(y_val):
                points.append({"x": round(x_val, 4), "y": round(y_val, 4)})
        except Exception:
            continue
    return points


def build_chart_config(spec):
    """
    spec: dict with a "type" of "bar", "line", "pie", or "function_graph".
    Returns a Chart.js-compatible config dict, or None if the spec is
    invalid/unsupported.

    Expected spec shapes:
      {"type": "bar"|"line"|"pie", "title": "", "labels": [...], "data": [...],
       "x_label": "", "y_label": ""}
      {"type": "function_graph", "title": "", "expression": "x^2 - 4",
       "x_min": -5, "x_max": 5, "x_label": "x", "y_label": "y"}
    """
    if not isinstance(spec, dict):
        return None
    kind = spec.get("type")

    if kind in ("bar", "line", "pie"):
        labels = spec.get("labels") or []
        data = spec.get("data") or []
        if not labels or not data or len(labels) != len(data):
            return None
        palette = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"]
        colors = [palette[i % len(palette)] for i in range(len(data))]
        dataset = {
            "label": spec.get("title", ""),
            "data": data,
            "backgroundColor": colors if kind != "line" else "rgba(37,99,235,0.15)",
            "borderColor": "#2563eb",
            "borderWidth": 2,
        }
        if kind == "line":
            dataset["fill"] = True
            dataset["tension"] = 0.3

        return {
            "type": kind,
            "data": {"labels": labels, "datasets": [dataset]},
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"display": kind == "pie"},
                    "title": {"display": bool(spec.get("title")), "text": spec.get("title", "")},
                },
                "scales": None if kind == "pie" else {
                    "x": {"title": {"display": bool(spec.get("x_label")), "text": spec.get("x_label", "")}},
                    "y": {"title": {"display": bool(spec.get("y_label")), "text": spec.get("y_label", "")}},
                },
            },
        }

    if kind == "function_graph":
        expression = spec.get("expression")
        if not expression:
            return None
        x_min = spec.get("x_min", -10)
        x_max = spec.get("x_max", 10)
        try:
            points = compute_function_points(expression, float(x_min), float(x_max))
        except Exception:
            return None
        if not points:
            return None

        return {
            "type": "line",
            "data": {
                "datasets": [{
                    "label": spec.get("title") or f"y = {expression}",
                    "data": points,
                    "borderColor": "#2563eb",
                    "backgroundColor": "rgba(37,99,235,0.08)",
                    "fill": True,
                    "tension": 0.35,
                    "pointRadius": 0,
                    "borderWidth": 2.5,
                }]
            },
            "options": {
                "responsive": True,
                "parsing": False,
                "plugins": {
                    "legend": {"display": True},
                    "title": {"display": bool(spec.get("title")), "text": spec.get("title", "")},
                },
                "scales": {
                    "x": {"type": "linear", "title": {"display": True, "text": spec.get("x_label", "x")}},
                    "y": {"title": {"display": True, "text": spec.get("y_label", "y")}},
                },
            },
        }

    return None
