
import json
from pathlib import Path


def generate_html(data, output_file):

    css = Path("assets/style.css").read_text(encoding="utf-8")
    js = Path("assets/script.js").read_text(encoding="utf-8")

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{data["metadata"]["topic"]}</title>

<style>

{css}

</style>

</head>

<body>

<div class="container">

<header>

<h1>{data["metadata"]["topic"]}</h1>

<h2>AI Powered Interactive Learning Material</h2>

</header>

<div class="info-card">

<p><strong>Instructor:</strong> {data["metadata"]["course_instructor"]}</p>

<p><strong>Department:</strong> {data["metadata"]["department"]}</p>

<p><strong>Programme:</strong> {data["metadata"]["programme"]}</p>

</div>

</div>

<script>

{js}

</script>

</body>

</html>
"""

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html)

    return output_file
