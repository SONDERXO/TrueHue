"""Use fixed v2 support; reuse sources/MST and preserve all v1 artifacts."""
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]


def main():
    parent=ROOT/'outputs/preferred_support_cohort_v2'
    importlib.import_module('340_prepare_preferred_reference_review').main(
        parent,ROOT/'outputs/preferred_reference_review_v2')
    importlib.import_module('339_rebuild_preferred_support_pairs').main(
        parent,ROOT/'outputs/preferred_support_pairs_v2',peribrow=True)


if __name__=='__main__':main()
