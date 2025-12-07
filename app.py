from flask import Flask, render_template, request

app = Flask(__name__)

def compute_items(lines):
    items = []
    total_percentage = 0.0

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            items.append({
                "name": f"Invalid line: {line}",
                "In_House": None,
                "Doordash": None,
                "Inflation_pct": None,
                "Check": None,
                "error": "Use: name,in_house,doordash"
            })
            continue

        name, in_house_str, doordash_str = parts
        try:
            in_house = float(in_house_str)
            doordash = float(doordash_str)
        except ValueError:
            items.append({
                "name": name,
                "In_House": None,
                "Doordash": None,
                "Inflation_pct": None,
                "Check": None,
                "error": "Numbers required"
            })
            continue

        if in_house == 0:
            items.append({
                "name": name,
                "In_House": in_house,
                "Doordash": doordash,
                "Inflation_pct": None,
                "Check": None,
                "error": "In_House cannot be 0"
            })
            continue

        inflation_pct = ((doordash - in_house) / in_house) * 100
        is_positive = inflation_pct > 0
        items.append({
            "name": name,
            "In_House": in_house,
            "Doordash": doordash,
            "Inflation_pct": inflation_pct,
            "Check": is_positive,
            "error": None
        })
        total_percentage += inflation_pct

    valid = [it for it in items if it["Inflation_pct"] is not None]
    avg_inflation = (sum(it["Inflation_pct"] for it in valid) / len(valid)) if valid else None

    return items, avg_inflation

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    raw_text = request.form.get("items_text", "")
    lines = raw_text.splitlines()
    items, avg_inflation = compute_items(lines)
    return render_template("result.html", items=items, avg_inflation=avg_inflation)
