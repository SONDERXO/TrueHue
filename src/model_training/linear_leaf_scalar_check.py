"""Independent scalar sufficient statistics and predictions. No array library."""
import math,struct
def f32(v):return struct.unpack('!f',struct.pack('!f',v))[0]
def coefficients(rows):
    n=len(rows);assert n>0
    x=[[f32(r['x'][j]) for j in [5,6]] for r in rows];y=[r['y'] for r in rows]
    mu=[math.fsum(r[j] for r in x)/n for j in range(2)]
    s=[math.sqrt(math.fsum((r[j]-mu[j])**2 for r in x)/n) for j in range(2)];s=[v if v else 1. for v in s]
    z=[[(r[j]-mu[j])/s[j] for j in range(2)] for r in x];b=[math.fsum(r[j] for r in y)/n for j in range(3)]
    a=math.fsum(r[0]**2 for r in z)/n+.01;c=math.fsum(r[1]**2 for r in z)/n+.01;d=math.fsum(r[0]*r[1] for r in z)/n;det=a*c-d*d
    assert det>0
    result=[]
    for k in range(3):
        h=[math.fsum(t[j]*(r[k]-b[k]) for t,r in zip(z,y))/n for j in range(2)]
        w=[(c*h[0]-d*h[1])/det/s[0],(a*h[1]-d*h[0])/det/s[1]]
        result.append([b[k]-math.fsum(mu[j]*w[j] for j in range(2)),*w])
    return result
def predict(tree,row):
    x=[f32(v) for v in row];i=0
    while tree['nodes'][i]['kind']=='split':
        n=tree['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
    result=[math.fsum([c[0],c[1]*x[5],c[2]*x[6]]) for c in tree['nodes'][i]['coefficients']]
    if any(not math.isfinite(v) or v<=0 for v in result):raise ValueError('Invalid controls')
    return i,result
