"""Generated-only mathematical probe; no dataset/model dependencies or reads."""
import hashlib
import json
import math
from pathlib import Path


def patch(material, light):
    return [[light[c] * (.2 * material[c] + .4 * k / 32)
             for c in range(3)] for k in range(33)]


def regress(pixels):
    totals = [sum(p) for p in pixels]
    if any(t <= 0 for t in totals):
        return {"available": False}
    x = [1 / t for t in totals]
    xm = math.fsum(x) / len(x)
    xx = math.fsum((v - xm) ** 2 for v in x)
    if xx == 0:
        return {"available": False}
    intercept, rms = [], []
    for c in range(3):
        y = [p[c] / t for p, t in zip(pixels, totals)]
        ym = math.fsum(y) / len(y)
        slope = math.fsum((a - xm) * (b - ym) for a, b in zip(x, y)) / xx
        b = ym - slope * xm
        intercept.append(b)
        rms.append(math.sqrt(math.fsum((v - (slope * u + b)) ** 2
                                      for u, v in zip(x, y)) / len(y)))
    return {"available": True, "intercept": intercept, "rms": rms}


def codes(pixels, encoding, role):
    exponent = 1 if encoding == "linear" else 1 / 2.2
    gamma = {"identity": 1, "under": 1 / .7, "over": .7, "cool": 1}[role]
    result = []
    for p in pixels:
        v = [a ** exponent for a in p]
        v = [a ** gamma for a in v]
        if role == "cool":
            v[0] *= 245 / 255
        result.append([round(255 * a) for a in v])
    return result


def main():
    root = Path(__file__).resolve().parents[1]
    protocol = root / "docs/highlight-context-generated-protocol-2026-11-13.md"
    out = root / "outputs/highlight_context_generated_math_v1"
    out.mkdir(exist_ok=False)
    materials = [( .6, .3, .2), (.3, .45, .2), (.2, .3, .55)]
    lights = [(1., 1., 1.), (245 / 255, 1., 1.)]
    records, checks = [], []
    for m, material in enumerate(materials):
        for l, light in enumerate(lights):
            p = patch(material, light)
            r = regress(p)
            expected = [v / sum(light) for v in light]
            maxerr = max(abs(a - b) for a, b in zip(r["intercept"], expected))
            # Independently solve the line from only the two endpoints.
            t0, t1 = sum(p[0]), sum(p[-1])
            endpoint = [(p[-1][c] - p[0][c]) / (t1 - t0) for c in range(3)]
            endpoint_error = max(abs(a - b) for a, b in zip(endpoint, expected))
            checks.append({"material": m, "light": l, "ideal_error": maxerr,
                           "endpoint_error": endpoint_error})
            assert maxerr < 1e-12 and endpoint_error < 1e-12
            for encoding in ("linear", "power_encoded"):
                for role in ("identity", "under", "over", "cool"):
                    rgb = codes(p, encoding, role)
                    result = regress([[v / 255 for v in row] for row in rgb])
                    records.append({"generated_fixture": True, "material": m,
                                    "light": l, "encoding": encoding, "role": role,
                                    "input_rgb8": rgb, **result})
        assert codes(patch(material, lights[0]), "linear", "cool") == codes(
            patch(material, lights[1]), "linear", "identity")
    assert len(records) == 48
    payload = {"generated_only": True, "record_count": len(records),
               "ideal_checks": checks, "exact_different_target_collisions": 3,
               "records": records,
               "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out / "records.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "ideal_checks": len(checks),
                      "exact_collisions": 3, "output": str(out)}))


if __name__ == "__main__":
    main()
