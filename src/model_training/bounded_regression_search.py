"""Budgeted non-greedy regression-tree search with exact rational leaf costs.

Only completed subproblems (or zero-cost certificates) enter the exact cache.
An interrupted search returns a feasible tree and a conservative zero bound.
This is an isolated development trainer; inference remains PortableTree.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import math
import time
from src.model_training.portable_tree import PortableTree, float32


class _Budget(Exception):
    pass


def search_tree(features, targets, incumbent, *, max_depth=4, max_states=5000,
                max_seconds=60., clock=time.monotonic):
    if type(max_depth) is not int or max_depth < 0 or type(max_states) is not int or max_states < 0:
        raise ValueError('Nonnegative integer depth/state limits required')
    if isinstance(max_seconds, bool) or not math.isfinite(max_seconds) or max_seconds <= 0:
        raise ValueError('Positive finite time budget required')
    seed=PortableTree(incumbent)
    x=[tuple(float32(v) for v in row) for row in features]
    raw_y=[tuple(row) for row in targets]
    if not x or len(x)!=len(raw_y) or any(len(row)!=len(seed.feature_names) for row in x):
        raise ValueError('Aligned nonempty feature/target rows required')
    if len(seed.target_names)!=3 or any(len(row)!=3 for row in raw_y):
        raise ValueError('Three correction controls required')
    if any(isinstance(v,bool) or not math.isfinite(v) or v<=0 for row in raw_y for v in row):
        raise ValueError('Positive finite numeric target controls required')
    y=[tuple(Fraction.from_float(float(v)) for v in row) for row in raw_y]
    full=(1<<len(x))-1
    def ids(mask):
        while mask:
            bit=mask & -mask; yield bit.bit_length()-1; mask-=bit
    leaf_cache={}
    def leaf(mask):
        if mask not in leaf_cache:
            counts=Counter(y[i] for i in ids(mask));n=sum(counts.values())
            means=tuple(sum((row[j]*count for row,count in counts.items()),Fraction())/n for j in range(3))
            cost=sum((count*sum(((row[j]-means[j])**2 for j in range(3)),Fraction()) for row,count in counts.items()),Fraction())
            leaf_cache[mask]=(cost,dict(values=[float(v) for v in means]))
        return leaf_cache[mask]
    def seed_node(index,mask,depth):
        if depth>max_depth:raise ValueError('Incumbent exceeds requested depth')
        node=incumbent['nodes'][index]
        if node['kind']=='leaf':
            if not mask:raise ValueError('Incumbent has empty fitting leaf')
            cost,optimal_leaf=leaf(mask)
            for a,b in zip(node['values'],optimal_leaf['values']):
                if not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12):
                    raise ValueError('Incumbent leaves must be fitting means')
            return cost,dict(values=list(node['values']))
        left=sum(1<<i for i in ids(mask) if x[i][node['feature']]<=node['threshold'])
        right=mask^left
        if not left or not right:raise ValueError('Incumbent split has empty fitting child')
        a,lt=seed_node(node['left'],left,depth+1);b,rt=seed_node(node['right'],right,depth+1)
        return a+b,dict(feature=node['feature'],threshold=node['threshold'],left=lt,right=rt)
    seed_cost,seed_nested=seed_node(0,full,0)
    root_cost,_=leaf(full);tolerance=1e-12*max(1.,float(root_cost))
    started=clock();memo={};expanded=0;partial=0;halted=None;root_updates=[]
    def check_time():
        nonlocal halted
        if clock()-started>=max_seconds:
            halted='time_limit';raise _Budget()
    def solve(mask,depth,warm=None,is_root=False):
        nonlocal expanded,partial,halted
        key=(mask,depth)
        if key in memo:return memo[key][0],memo[key][1],True
        cost,tree=leaf(mask)
        if warm is not None and warm[0]<=cost:cost,tree=warm
        # These exact base cases require no tree search.
        if depth==0 or cost==0:
            memo[key]=(cost,tree);return cost,tree,True
        complete=True
        try:
            check_time()
            if expanded>=max_states:
                halted='state_limit';raise _Budget()
            expanded+=1;cuts=[];seen=set()
            members=list(ids(mask))
            for feature in range(len(x[0])):
                check_time();ordered=sorted(members,key=lambda i:x[i][feature]);left=0
                for k,i in enumerate(ordered[:-1]):
                    check_time()
                    left|=1<<i;lv=x[i][feature];rv=x[ordered[k+1]][feature]
                    if rv<=lv+1e-7 or left in seen:continue
                    seen.add(left);right=mask^left
                    # Ordering affects speed only; all cuts remain eligible.
                    immediate=leaf(left)[0]+leaf(right)[0]
                    cuts.append((immediate,feature,(lv+rv)/2,left,right))
            for _,feature,threshold,left,right in sorted(cuts,key=lambda c:(c[0],c[1],c[2])):
                check_time()
                lc,lt,le=solve(left,depth-1)
                if halted:
                    rc,rt=leaf(right);re=False
                else:rc,rt,re=solve(right,depth-1)
                candidate=lc+rc
                if candidate<cost:
                    cost=candidate;tree=dict(feature=feature,threshold=threshold,left=lt,right=rt)
                    if is_root:root_updates.append(float(cost))
                if cost==0:complete=True;break
                if halted or not le or not re:complete=False;break
        except _Budget:complete=False
        if complete or cost==0:
            memo[key]=(cost,tree);return cost,tree,True
        partial+=1
        return cost,tree,False
    best_cost,best_tree,exact=solve(full,max_depth,(seed_cost,seed_nested),True)
    improved=float(seed_cost-best_cost)>tolerance
    if not improved:
        payload=deepcopy(incumbent);selected_cost=seed_cost
    else:
        nodes=[]
        def emit(tree):
            index=len(nodes);nodes.append(None)
            if 'values' in tree:nodes[index]=dict(kind='leaf',values=tree['values'])
            else:
                left=emit(tree['left']);right=emit(tree['right'])
                nodes[index]=dict(kind='split',feature=tree['feature'],threshold=tree['threshold'],left=left,right=right)
            return index
        emit(best_tree);payload=deepcopy(incumbent);payload['nodes']=nodes
        payload['provenance']=dict(objective='unweighted_raw_three_control_SSE',trainer='bounded_non_greedy_regression_search_v1',runtime_adopted=False)
        selected_cost=best_cost
    portable=PortableTree(payload)
    # Evaluate serialized floating leaves separately from the exact-mean objective.
    exported_cost=sum((sum(((Fraction.from_float(float(v))-target)**2 for v,target in zip(portable.predict_one(row),yi)),Fraction()) for row,yi in zip(x,y)),Fraction())
    stats=dict(status='completed' if exact else 'budget_limited',limit_reason=halted,
        expanded_states=expanded,completed_cached_states=len(memo),interrupted_states_not_cached=partial,
        partial_states_cached=0,elapsed_seconds=clock()-started,initial_SSE=float(seed_cost),
        best_found_SSE=float(best_cost),selected_SSE=float(selected_cost),exported_float_SSE=float(exported_cost),
        global_lower_bound=float(best_cost) if exact else 0.,optimality_certified=exact,
        selected_optimality_certified=exact and selected_cost==best_cost,
        optimality_scope='unrounded_leaf_means_within_declared_fitting_partition_class',
        selected_is_best_found=improved or best_cost==seed_cost,strict_improvement=improved,
        numerical_improvement_tolerance=tolerance,root_improvements=root_updates,
        state_limit=max_states,time_limit_seconds=max_seconds,incumbent_refitted=False,
        initial_SSE_exact=[str(seed_cost.numerator),str(seed_cost.denominator)],
        best_found_SSE_exact=[str(best_cost.numerator),str(best_cost.denominator)])
    return dict(tree=payload,search=stats)
