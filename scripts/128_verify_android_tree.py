"""Compile the Android tree core on a real JVM and compare frozen Python vectors."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.portable_tree import PortableTree


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError('Output exists; choose a new directory')
    model_path = ROOT / 'outputs/core_tree_portability_v2/decision_tree.json'
    verification_path = model_path.with_name('verification.json')
    verification = json.loads(verification_path.read_text())
    assert digest(model_path) == verification['export_sha256']
    payload = json.loads(model_path.read_text())
    tree = PortableTree(payload)
    source = ROOT / 'android-app/app/src/main/java/com/example/skintonecorrection/ml/PortableRegressionTree.java'
    vectors = [r['features'] for r in verification['records'] + verification['boundary_cases']]
    # Also witness double values around every threshold that round at float32 input.
    for node in payload['nodes']:
        if node['kind'] == 'split':
            for value in [math.nextafter(node['threshold'], -math.inf), node['threshold'], math.nextafter(node['threshold'], math.inf)]:
                row = list(vectors[0]); row[node['feature']] = value; vectors.append(row)
    nodes = []
    for n in payload['nodes']:
        if n['kind'] == 'leaf':
            nodes.append('Node.leaf(' + ','.join(repr(v) for v in n['values']) + ')')
        else:
            nodes.append(f'Node.split({n["feature"]},{n["threshold"]!r},{n["left"]},{n["right"]})')
    java = '''import com.example.skintonecorrection.ml.PortableRegressionTree;
import com.example.skintonecorrection.ml.PortableRegressionTree.Node;
public class TreeParity {
 static int rejected=0;
 static void reject(Runnable action) { try { action.run(); } catch(IllegalArgumentException e) { rejected++; return; } throw new AssertionError("Accepted invalid input"); }
 public static void main(String[] args) {
 Node[] nodes = new Node[]{NODES};
 PortableRegressionTree tree = new PortableRegressionTree(nodes,4,3);
 double[][] vectors = new double[][]{VECTORS};
 for(double[] x:vectors) {
  double[] y=tree.predict(x);
  System.out.println(tree.leafId(x)+","+y[0]+","+y[1]+","+y[2]);
 }
 reject(()->tree.predict(new double[]{Double.NaN,0,0,0}));
 reject(()->tree.predict(new double[]{0,0,0,Double.POSITIVE_INFINITY}));
 reject(()->tree.predict(new double[]{Double.MAX_VALUE,0,0,0}));
 reject(()->tree.predict(new double[]{0,0,0}));
 reject(()->tree.predict(null));
 reject(()->new PortableRegressionTree(new Node[]{Node.split(0,0,0,0)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.split(0,0,1,1),Node.leaf(1,1,1)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.leaf(1,1,1),Node.leaf(1,1,1)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.leaf(0,1,1)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.leaf(1,1)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.split(4,0,1,2),Node.leaf(1,1,1),Node.leaf(1,1,1)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.split(0,Double.NaN,1,2),Node.leaf(1,1,1),Node.leaf(1,1,1)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.split(0,0,1,5),Node.leaf(1,1,1)},4,3));
 reject(()->new PortableRegressionTree(new Node[]{null},4,3));
 reject(()->new PortableRegressionTree(new Node[]{Node.leaf(1,1,Double.NaN)},4,3));
 double[] original=tree.predict(vectors[0]); original[0]=999;
 if(tree.predict(vectors[0])[0]==999)throw new AssertionError("Mutable prediction");
 nodes[0]=null;
 if(tree.predict(vectors[0])[0]==999)throw new AssertionError("Mutable graph");
 System.out.println("rejected="+rejected);
 }
}'''.replace('NODES', ','.join(nodes)).replace('VECTORS', ','.join('new double[]{' + ','.join(repr(v) for v in x) + '}' for x in vectors))
    args.output_dir.mkdir(parents=True)
    harness = args.output_dir / 'TreeParity.java'; harness.write_text(java)
    classes = args.output_dir / 'classes'; classes.mkdir()
    subprocess.run([str(args.jdk / 'bin/javac.exe'), '--release', '11', '-d', str(classes), str(source), str(harness)], check=True, capture_output=True, text=True)
    run = subprocess.run([str(args.jdk / 'bin/java.exe'), '-cp', str(classes), 'TreeParity'], check=True, capture_output=True, text=True)
    lines = run.stdout.splitlines()
    assert len(lines) == len(vectors) + 1 and lines[-1] == 'rejected=15'
    for x, line in zip(vectors, lines):
        values = line.split(',')
        assert int(values[0]) == tree.leaf_id(x)
        assert [float(v) for v in values[1:]] == tree.predict_one(x)
    (args.output_dir / 'jvm_output.txt').write_text(run.stdout)
    assets = ROOT / 'android-app/app/src/main/assets'
    assets.mkdir(exist_ok=True)
    # These files are development packaging, not a replacement trained model.
    for target, content in [(assets / 'decision_tree.json', model_path.read_bytes()),
                            (assets / 'decision_tree.sha256', (digest(model_path) + '\n').encode())]:
        if target.exists() and target.read_bytes() != content:
            raise ValueError(f'Refusing to replace a different asset: {target}')
        target.write_bytes(content)
    result = dict(status='pass_jvm_core_only', saved_vectors=23, boundary_vectors=12,
        additional_double_rounding_vectors=len(vectors)-35, invalid_cases_rejected=15,
        predictions_and_leaf_ids_exact=True, max_parameter_difference=0,
        apk_built=False, device_tested=False, android_json_loader_compiled=False,
        new_model_fits=0, mst_available=False,
        input_sha256={str(p.relative_to(ROOT)): digest(p) for p in [source, model_path, verification_path, Path(__file__)]},
        jdk_version=subprocess.run([str(args.jdk / 'bin/java.exe'), '-version'],capture_output=True,text=True,check=True).stderr)
    (args.output_dir / 'verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
