from flask import Flask, jsonify, request, send_from_directory

from planner import PlanRequest, generate_week_plan

app = Flask(__name__, static_folder="static")

LIMITS = {
    "budget": (10.0, 1000.0, float),
    "people": (1, 8, int),
    "kcal_target": (1200, 4000, int),
    "protein_target": (30, 300, int),
    "max_stores": (1, 3, int),
}


def _parse(payload: dict) -> PlanRequest:
    values = {}
    for name, (lo, hi, cast) in LIMITS.items():
        if name not in payload:
            continue
        try:
            value = cast(payload[name])
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be a number.")
        if not lo <= value <= hi:
            raise ValueError(f"{name} must be between {lo} and {hi}.")
        values[name] = value
    return PlanRequest(**values)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/plan")
def plan():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify(error="Request body must be a JSON object."), 400
    try:
        req = _parse(payload)
        return jsonify(generate_week_plan(req))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


if __name__ == "__main__":
    app.run(debug=False)
