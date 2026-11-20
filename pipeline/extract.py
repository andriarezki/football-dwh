"""Extract: land raw season CSVs in a partitioned data-lake layout (S3-style keys) with a manifest.
Idempotent: files are copied only when the SHA-256 changed."""
import hashlib, json, shutil, sys
from pathlib import Path

LAKE = Path("lake/raw")

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def land(source_dir: str) -> dict:
    manifest_path = LAKE / "_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    changed = []
    for f in sorted(Path(source_dir).glob("E0_*.csv")):
        code = f.stem.split("_")[1]
        dest = LAKE / f"season={code}" / f.name
        digest = sha256(f)
        if manifest.get(f.name) == digest and dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        manifest[f.name] = digest
        changed.append(f.name)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return {"changed": changed, "total": len(manifest)}

if __name__ == "__main__":
    print(land(sys.argv[1] if len(sys.argv) > 1 else "source"))
