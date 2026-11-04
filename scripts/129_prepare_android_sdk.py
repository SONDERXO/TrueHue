"""Download official pinned command-line tools into the ignored workspace SDK."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://dl.google.com/android/repository/'


def main():
    folder = ROOT / 'outputs/android_toolchain'
    folder.mkdir(parents=True, exist_ok=True)
    metadata = urllib.request.urlopen(BASE + 'repository2-1.xml', timeout=60).read()
    (folder / 'repository2-1.xml').write_bytes(metadata)
    root = ET.fromstring(metadata)
    package = next(p for p in root.iter() if p.tag.endswith('remotePackage') and p.get('path') == 'cmdline-tools;19.0')
    archive = next(a for a in package.findall('./archives/archive') if a.findtext('host-os') == 'windows')
    complete = archive.find('complete')
    filename = complete.findtext('url')
    assert filename and '/' not in filename and filename.endswith('.zip')
    expected_size = int(complete.findtext('size'))
    checksum = complete.find('checksum')
    algorithm = checksum.get('type', 'sha1')
    assert algorithm in ('sha1', 'sha256')
    download = folder / filename
    if not download.exists():
        temporary = download.with_suffix('.partial')
        with urllib.request.urlopen(BASE + filename, timeout=120) as response, temporary.open('wb') as stream:
            while block := response.read(1024 * 1024):
                stream.write(block)
        temporary.replace(download)
    assert download.stat().st_size == expected_size
    assert hashlib.new(algorithm, download.read_bytes()).hexdigest() == checksum.text.strip()
    target = folder / 'sdk/cmdline-tools/19.0'
    if not target.exists():
        target.mkdir(parents=True)
        with zipfile.ZipFile(download) as zipped:
            for entry in zipped.infolist():
                path = PurePosixPath(entry.filename)
                if path.parts[0] != 'cmdline-tools' or path.is_absolute() or '..' in path.parts:
                    raise ValueError('Unexpected archive path')
                destination = target.joinpath(*path.parts[1:])
                assert destination.resolve().is_relative_to(target.resolve())
                if entry.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(zipped.read(entry))
    assert (target / 'bin/sdkmanager.bat').is_file()
    result = dict(package='cmdline-tools;19.0', url=BASE + filename,
                  size=expected_size, publisher_checksum_algorithm=algorithm,
                  publisher_checksum=checksum.text.strip(),
                  sha256=hashlib.sha256(download.read_bytes()).hexdigest(),
                  sdk_root=str((folder / 'sdk').resolve()), licenses_accepted_by_script=False)
    (folder / 'commandline_tools_provenance.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
