"""Restore only pinned public support metadata needed by the original FFHQ downloader."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'docs/third-party/ffhq-repository-4826aa6.json'
    target=ROOT/'outputs/dataset_role_assessment_20261103_v1/ffhq-repository.json'
    data=source.read_bytes()
    if target.exists():
        if target.read_bytes()!=data:
            raise ValueError('Existing metadata differs; refusing to overwrite research evidence')
        print('Pinned FFHQ support metadata already matches; unchanged.')
        return
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
    assert target.read_bytes()==data
    note=target.parent/'COLLABORATOR_METADATA_ONLY.txt'
    note.write_text('Only the pinned public FFHQ repository tree was restored for source download.\n'
        'This is not the complete historical dataset-role assessment or a new experiment.\n'
        'Provenance and licence: docs/third-party/ffhq-support-metadata.md\n',encoding='utf-8')
    print('Restored support metadata only; no photos, models, labels or experiment results downloaded.')
    print('SHA256: '+hashlib.sha256(data).hexdigest())


if __name__=='__main__':main()
