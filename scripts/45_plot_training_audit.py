"""Standalone coverage figures from the completed read-only tree audit."""
import csv
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from src.utilities.config import get_config


def read(path):
    with path.open(newline='',encoding='utf-8') as stream:return list(csv.DictReader(stream))


def main():
    out=ROOT/get_config().OUTPUTS_ROOT/'training_tree_audit_v1'
    if (out/'coverage_and_routing.png').exists():raise FileExistsError('Audit plot exists')
    summary=json.loads((out/'summary.json').read_text());coverage=read(out/'variant_coverage.csv');traces=read(out/'pair_traces.csv');sources=read(out/'source_routing.csv')
    colors=dict(dark='#3267a6',bright_warm='#d87924',color_shift='#7b52a0')
    names=('dark','bright_warm','color_shift');splits=('train','development_validation','stress_only','excluded')
    split_colors=('#3b8b75','#748ca0','#dc9b3e','#ba6470')
    fig,axes=plt.subplots(1,3,figsize=(16,5.6),layout='constrained')
    bottoms=np.zeros(3)
    for split,color,label in zip(splits,split_colors,('Train','Development validation','Clipped stress','Excluded input')):
        values=np.array([next(int(r['pairs']) for r in coverage if r['variant']==variant and r['table_use']==split) for variant in names])
        bars=axes[0].bar(np.arange(3),values,bottom=bottoms,color=color,label=label)
        for bar,value,bottom in zip(bars,values,bottoms):
            if value:axes[0].text(bar.get_x()+bar.get_width()/2,bottom+value/2,str(value),ha='center',va='center',color='white',fontweight='bold')
        bottoms+=values
    axes[0].set_xticks(range(3),('Darkened','Bright / warm','Color shift'));axes[0].set_ylabel('Pair count')
    axes[0].set_title('Only 3 bright/warm pairs reach training');axes[0].legend(fontsize=7,loc='upper center',bbox_to_anchor=(.5,-.15),ncol=2,frameon=False)
    markers=dict(train='o',development_validation='^',stress_only='X')
    for row in traces:
        axes[1].scatter(float(row['input_mean_b_star']),float(row['input_mean_l_star']),
            c=colors[row['variant']],marker=markers[row['table_use']],s=55 if row['table_use']=='train' else 85,
            edgecolors='white' if row['table_use']=='train' else '#17212a',linewidths=.6)
        if row['table_use']=='stress_only':
            short=row['pair_id'].split('train_')[1].split('.')[0]
            axes[1].annotate(short,(float(row['input_mean_b_star']),float(row['input_mean_l_star'])),xytext=(3,4),textcoords='offset points',fontsize=7)
    paths=json.loads((out/'exact_paths.json').read_text());rules={r['feature']:r['threshold'] for p in paths for r in p['path']}
    lo=summary['feature_training_ranges']['input_mean_b_star']['min'];hi=max(float(r['input_mean_b_star']) for r in traces)+2
    root=rules['input_mean_l_star'];bcut=rules['input_mean_b_star']
    axes[1].axhline(root,color='#526371',linestyle='--',linewidth=.9)
    axes[1].plot([bcut,bcut],[root,axes[1].get_ylim()[1]],color='#526371',linestyle='--',linewidth=.9)
    axes[1].set_xlim(lo-2,hi);axes[1].set_xlabel('Input mean b*');axes[1].set_ylabel('Input mean L*')
    axes[1].set_title('Bright stress cases reach a dark-only leaf')
    handles=[Line2D([],[],marker='o',linestyle='',color=colors[k],label=k.replace('_',' ')) for k in names]
    handles += [Line2D([],[],marker=m,linestyle='',color='#475865',label=k.replace('_',' ')) for k,m in markers.items()]
    axes[1].legend(handles=handles,fontsize=7,loc='lower right')
    axes[1].text(.02,.02,'Projection only: the a* split is not shown',transform=axes[1].transAxes,fontsize=7)
    bright=[r for r in sources if r['variant']=='bright_warm']
    for row in bright:
        split=row['table_use'];color=split_colors[splits.index(split)]
        axes[2].scatter(float(row['source_reference_l_star_audit_only']),float(row['input_l_star']),color=color,
                        marker=markers.get(split,'s'),s=80,edgecolors='#17212a',linewidths=.6)
        short=row['source_image_id'].split('/')[-1].split('.')[0]
        axes[2].annotate(short,(float(row['source_reference_l_star_audit_only']),float(row['input_l_star'])),xytext=(4,4),textcoords='offset points',fontsize=7)
    axes[2].set_xlabel('Source reference mean L* (audit only)');axes[2].set_ylabel('Bright/warm input mean L*')
    axes[2].set_title('Clipping routing removes a source range')
    axes[2].text(.02,.98,'Reference values never enter model inputs\nNo MST or demographic labels assigned',transform=axes[2].transAxes,fontsize=7,va='top',bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
    for ax in axes:ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Frozen prototype training audit — no refit or tuning',fontsize=15)
    fig.savefig(out/'coverage_and_routing.png',dpi=150);fig.savefig(out/'coverage_and_routing.svg')
    plt.close(fig)
    print('Saved standalone PNG and SVG audit figures.')


if __name__=='__main__':main()
