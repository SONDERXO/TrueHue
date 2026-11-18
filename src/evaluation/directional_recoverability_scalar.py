"""Independent scalar formulas and objective; no optimizer or production workflow imports."""
import math
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000


def distortion(reference, role):
    output = np.empty_like(reference)
    clipped = np.zeros(reference.shape, bool)
    for y, x, c in np.ndindex(reference.shape):
        value = int(reference[y, x, c]) / 255
        if role in ('exposure_under', 'combined_under'):
            value = (1 + 8 / 100) * (math.pow(value, 1 / .7) - 1) + 1 - 35 / 255
        elif role in ('exposure_over', 'combined_over'):
            value = (1 + 8 / 100) * math.pow(value, .7) + 35 / 255
        if role in ('colour_only', 'combined_under', 'combined_over'):
            value += (-10, 0, 10)[c] / 255
        clipped[y, x, c] = value < 0 or value > 1
        output[y, x, c] = round(255 * min(1., max(0., value)))
    return output, clipped


def correction(image, alpha, parameters, reference):
    output = np.empty_like(image)
    squares = []
    for y, x, c in np.ndindex(image.shape):
        value = int(image[y, x, c]) / 255
        transformed = math.pow(value, parameters[0]) * (parameters[1], 1., parameters[2])[c]
        mixed = (1 - float(alpha[y, x])) * value + float(alpha[y, x]) * min(1., max(0., transformed))
        output[y, x, c] = round(255 * mixed)
        if alpha[y, x] > 0:
            squares.append((mixed - int(reference[y, x, c]) / 255) ** 2)
    return output, math.sqrt(math.fsum(squares) / len(squares))


def metrics(image, reference, mask):
    selected = list(zip(image[mask], reference[mask]))
    if not selected:
        return None
    error = math.fsum(abs(int(a[c]) - int(b[c])) for a, b in selected for c in range(3)) / (3 * len(selected))
    # Independent full-image conversion/selection versus production selected-pixel conversion.
    delta = deltaE_ciede2000(rgb2lab(image / 255.), rgb2lab(reference / 255.))
    return {'RGB': error, 'DE': math.fsum(float(v) for v in delta[mask]) / len(selected)}


def verify(source, record, image, output):
    reference, alpha = source['reference'], source['alpha']
    generated, clipped = distortion(reference, record['role'])
    np.testing.assert_array_equal(image, generated)
    for name, mask in {'whole': np.ones(alpha.shape, bool), 'primary': alpha > 0}.items():
        assert record['clipping'][name] == {'channels': int(clipped[mask].sum()),
            'pixels': int(clipped.any(axis=2)[mask].sum())}
    target = record['target']
    if target['parameters'] is None:
        assert output is None
    else:
        expected, rmse = correction(image, alpha, target['parameters'], reference)
        np.testing.assert_array_equal(output, expected)
        if 'float_rmse' in target:
            assert math.isclose(rmse, target['float_rmse'], abs_tol=1e-12, rel_tol=1e-12)
        assert np.array_equal(output[alpha == 0], image[alpha == 0])
        assert np.array_equal(output[source['protected']], image[source['protected']])
    masks = {'primary': alpha > 0, 'core': alpha == 1, 'feather': (alpha > 0) & (alpha < 1),
             'whole': np.ones(alpha.shape, bool)}
    for name, mask in masks.items():
        saved = record['regions'][name]
        assert saved['pixels'] == int(mask.sum())
        for label, values in [('input', image), ('output', output)]:
            expected = metrics(values, reference, mask) if values is not None else None
            actual = saved[label]
            if expected is None:
                assert actual is None
            else:
                for key, value in expected.items():
                    assert math.isclose(actual[key], value, abs_tol=1e-10, rel_tol=1e-10)
        if saved['benefit'] is not None:
            for key, value in saved['benefit'].items():
                assert math.isclose(value, saved['input'][key] - saved['output'][key], abs_tol=1e-12)
            count = int(mask.sum()) * 3
            change = math.fsum(abs(int(a) - int(b)) for a, b in zip(output[mask].flat, image[mask].flat)) / count
            assert math.isclose(change, saved['change_RGB'], abs_tol=1e-12)
    return True
