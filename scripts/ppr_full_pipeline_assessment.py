"""One frozen PPR mapping assessment, with generated checks before portrait access."""
from pathlib import Path
import sys
import json
import math
import hashlib
import zipfile
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ASSETS = ROOT / 'outputs/ppr_full_pipeline_assets_v1'
QA = ROOT / 'outputs/ppr_full_pipeline_engineering_v1'
OUT = ROOT / 'outputs/ppr_full_pipeline_prediction_v1'
WB = ROOT / 'outputs/wb_feature_direct_prediction_v1'
FEATURES = ROOT / 'outputs/ppr_parameter_features_v1'
PROTOCOL = ROOT / 'docs/ppr-full-pipeline-assessment-protocol-2026-11-17.md'
ROLES = ['identity', 'colour_only', 'exposure_under', 'exposure_over', 'combined_under', 'combined_over']
F = np.float32
BIN = F(1.000001 / 32)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_sha(value):
    return hashlib.sha256(value.tobytes()).hexdigest()


def runtime():
    torch.set_num_threads(2)
    receipt = read(ASSETS / 'build_receipt.json')
    assert receipt['passed'] and sha(ASSETS / 'build/build.log') == receipt['log_sha256']
    extension = ROOT / receipt['extension']
    assert sha(extension) == receipt['extension_sha256']
    for name, digest in receipt['source_sha256'].items():
        assert sha(ASSETS / 'build/source' / name) == digest
    assert sha(ASSETS / 'LUTs_-1.pth') == read(ASSETS / 'lut_receipt.json')['sha256']
    assert sha(PROTOCOL) == read(ASSETS / 'lut_receipt.json')['protocol_sha256']
    state = torch.load(ASSETS / 'LUTs_-1.pth', map_location='cpu', weights_only=True)
    assert set(state) == set('12345')
    luts = [state[k]['LUT'].contiguous() for k in '12345']
    assert all(t.dtype == torch.float32 and tuple(t.shape) == (3, 33, 33, 33)
               and torch.isfinite(t).all() for t in luts)
    sys.path.insert(0, str(extension.parent))
    import trilinear
    return trilinear, luts


def validate(x, coefficients):
    if (not isinstance(x, torch.Tensor) or x.dtype != torch.float32 or x.device.type != 'cpu'
            or x.ndim != 4 or x.shape[:2] != (1, 3) or min(x.shape[2:]) < 1
            or not x.is_contiguous() or not torch.isfinite(x).all()
            or torch.any(x < 0) or torch.any(x > 1)):
        raise ValueError('Contiguous finite CPU float32 single NCHW RGB image in [0,1] required')
    c = np.asarray(coefficients)
    if c.dtype != np.float32 or c.shape != (5,) or not np.isfinite(c).all():
        raise ValueError('Five finite raw float32 coefficients required')
    return c


def native(module, luts, x, coefficients):
    c = validate(x, coefficients)
    terms = []
    with torch.no_grad():
        for lut, weight in zip(luts, c):
            output = torch.empty_like(x)
            assert module.forward(lut, x, output, 33, 33 ** 3, float(BIN), x.shape[3], x.shape[2], 1) == 1
            terms.append(output * float(weight))
        result = terms[0]
        for term in terms[1:]:
            result = result + term
    assert torch.isfinite(result).all()
    return result[0].permute(1, 2, 0).contiguous().numpy()


def scalar(luts, x, coefficients):
    """Independent scalar indexing and float32 arithmetic in official operation order."""
    image = x[0].permute(1, 2, 0).numpy()
    tables = [t.numpy().reshape(3, -1) for t in luts]
    output = np.empty_like(image)
    corners = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0),
               (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
    for iy in range(image.shape[0]):
        for ix in range(image.shape[1]):
            rgb = image[iy, ix]
            base = [math.floor(float(F(v / BIN))) for v in rgb]
            fraction = [F(np.fmod(v, BIN) / BIN) for v in rgb]
            weights = []
            indices = []
            for dr, dg, db in corners:
                factors = [fraction[j] if d else F(F(1) - fraction[j])
                           for j, d in enumerate((dr, dg, db))]
                weights.append(F(F(factors[0] * factors[1]) * factors[2]))
                indices.append(base[0] + dr + (base[1] + dg) * 33 + (base[2] + db) * 33 ** 2)
            for channel in range(3):
                mixed = F(0)
                for table_index, table in enumerate(tables):
                    value = F(weights[0] * table[channel, indices[0]])
                    for k in range(1, 8):
                        value = F(value + F(weights[k] * table[channel, indices[k]]))
                    term = F(value * coefficients[table_index])
                    mixed = term if table_index == 0 else F(mixed + term)
                output[iy, ix, channel] = mixed
    return output


def quantize(raw):
    return np.clip(raw * F(255) + F(.5), 0, 255).astype(np.uint8)


def composite(image, native_rgb, alpha, protected):
    if (image.dtype != np.uint8 or native_rgb.dtype != np.uint8 or image.shape != native_rgb.shape
            or alpha.shape != image.shape[:2] or protected.shape != alpha.shape
            or protected.dtype != bool or not np.issubdtype(alpha.dtype, np.floating)
            or not np.isfinite(alpha).all() or (alpha < 0).any() or (alpha > 1).any()
            or (alpha[protected] != 0).any()):
        raise ValueError('Unchanged matching RGB8, alpha and protection required')
    a = alpha.astype(np.float64)[..., None]
    result = np.rint((1 - a) * image + a * native_rgb).astype(np.uint8)
    result[(alpha == 0) | protected] = image[(alpha == 0) | protected]
    return result


def bindings():
    paths = [Path(__file__), PROTOCOL, ASSETS / 'build_receipt.json', ASSETS / 'LUTs_-1.pth',
             ASSETS / 'lut_inspection.json', ASSETS / 'user_authorization.json']
    paths.append(ROOT / read(ASSETS / 'build_receipt.json')['extension'])
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}


def generated():
    if QA.exists():
        raise FileExistsError(QA)
    QA.mkdir()
    try:
        module, luts = runtime()
        before = [array_sha(t.numpy()) for t in luts]
        codes = np.arange(256, dtype=np.uint8)
        first = np.stack([codes, np.roll(codes, 37), 255 - codes], axis=1)[None, ...]
        rng = np.random.default_rng(42)
        images = [np.repeat(first, 3, axis=0), rng.integers(0, 256, (11, 29, 3), dtype=np.uint8),
                  rng.integers(0, 256, (9, 33, 3), dtype=np.uint8)]
        coefficients = [np.array(c, np.float32) for c in [(1.2, -.3, .2, -.1, .05),
                        (1.5, -.2, -.4, -1.2, -.4), (.8, .1, -.2, .3, -.1)]]
        records = []
        for image, c in zip(images, coefficients):
            x = torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1)[None])).float() / 255
            input_hash = array_sha(x.numpy())
            a = native(module, luts, x, c)
            b = scalar(luts, x, c)
            error = float(np.max(np.abs(a.astype(float) - b)))
            assert error <= 1e-6 and np.array_equal(quantize(a), quantize(b))
            for _ in range(2):
                assert np.array_equal(a, native(module, luts, x, c))
            assert input_hash == array_sha(x.numpy())
            alpha = np.tile(np.linspace(0, 1, image.shape[1]), (image.shape[0], 1))
            protected = np.zeros(alpha.shape, bool)
            protected[0] = True
            alpha[protected] = 0
            rgb = quantize(a)
            result = composite(image, rgb, alpha, protected)
            independent = np.empty_like(result)
            for iy, ix, channel in np.ndindex(result.shape):
                z = float(alpha[iy, ix])
                independent[iy, ix, channel] = round((1 - z) * int(image[iy, ix, channel]) + z * int(rgb[iy, ix, channel]))
                value = F(F(a[iy, ix, channel] * F(255)) + F(.5))
                assert int(rgb[iy, ix, channel]) == int(min(255, max(0, value)))
            assert np.array_equal(result, independent)
            assert np.array_equal(result[protected], image[protected])
            records.append(dict(shape=list(image.shape), max_float_error=error, exact_RGB8=True,
                                exact_composite=True, repeats=2, input_immutable=True))
        # Floating near-grid inputs exercise cells that integer image codes cannot cover.
        edges = [F(0), F(1)]
        for k in range(1, 32):
            value = F(F(k) * BIN)
            edges.extend([np.nextafter(value, F(0)), value, np.nextafter(value, F(1))])
        e = np.asarray(edges, np.float32)
        boundary = np.stack([e, np.roll(e, 13), np.roll(e, 29)])[None, :, None, :]
        x = torch.from_numpy(np.ascontiguousarray(boundary))
        a = native(module, luts, x, coefficients[0])
        b = scalar(luts, x, coefficients[0])
        boundary_error = float(np.max(np.abs(a.astype(float) - b)))
        assert boundary_error <= 1e-6 and np.array_equal(quantize(a), quantize(b))
        invalid = [x.double(), x.repeat(2, 1, 1, 1), x[:, :2].contiguous(), x.clone(), x.clone(), x.clone()]
        invalid[-3][0, 0, 0, 0] = float('nan')
        invalid[-2][0, 0, 0, 0] = -0.01
        invalid[-1][0, 0, 0, 0] = 1.01
        rejected = 0
        for bad in invalid:
            try:
                native(None, luts, bad, coefficients[0])
            except ValueError:
                rejected += 1
            else:
                raise AssertionError('Invalid input reached native code')
        for c in [np.zeros(4, np.float32), np.zeros(5, np.float64), np.full(5, np.nan, np.float32)]:
            try:
                native(None, luts, x, c)
            except ValueError:
                rejected += 1
            else:
                raise AssertionError('Invalid coefficients reached native code')
        assert before == [array_sha(t.numpy()) for t in luts]
        write(QA / 'verification.json', dict(passed=True, generated_records=records,
              boundary_samples=len(edges), boundary_max_float_error=boundary_error,
              all_256_codes_each_channel=True, invalid_rejected_before_native=rejected,
              all_five_LUTs_immutable=True, actual_image_calls=0, new_training=0, bindings=bindings()))
        print('PASS generated native/scalar interpolation, exact RGB8/composite, repeats/guards/immutability.', flush=True)
    except Exception as error:
        write(QA / 'failure.json', dict(error=repr(error), actual_image_calls=0))
        raise


if __name__ == '__main__':
    {'generated': generated}[sys.argv[1]]()
