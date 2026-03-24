import json
import re
from pathlib import Path

ROOT = Path(".")
IGNORE = {".github", "scripts", ".git"}


def parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    
    fm = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"')
        
        # tags: ["ai", "agents"] → список
        if val.startswith("["):
            val = [t.strip().strip('"').strip("'") for t in val.strip("[]").split(",")]
        
        fm[key] = val
    return fm


def make_note(md_file: Path) -> dict | None:
    text = md_file.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if not fm:
        print(f"  ⚠️  нет frontmatter: {md_file}")
        return None

    slug = str(md_file.with_suffix(""))  # git/module_1_1 и т.д.

    return {
        "slug": slug,
        "title": fm.get("title", slug),
        "description": fm.get("description", ""),
        "date": fm.get("date", ""),
        "tags": fm.get("tags", []),
        "file": str(md_file),
    }


def build_manifest() -> dict:
    # Загружаем существующий manifest чтобы не потерять title/description репо
    manifest_path = ROOT / "manifest.json"
    existing = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    root_notes = []
    folders = []

    for item in sorted(ROOT.iterdir()):
        if item.name in IGNORE or item.name.startswith("."):
            continue

        if item.is_file() and item.suffix == ".md":
            note = make_note(item)
            if note:
                root_notes.append(note)

        elif item.is_dir():
            folder_notes = []
            for md_file in sorted(item.rglob("*.md")):
                note = make_note(md_file)
                if note:
                    folder_notes.append(note)

            if folder_notes:
                folders.append({
                    "slug": item.name,
                    "title": item.name.capitalize(),
                    "notes": folder_notes,
                })

    return {
        "title": existing.get("title", "Мои заметки"),
        "description": existing.get("description", ""),
        "notes": root_notes,
        "folders": folders,
    }


if __name__ == "__main__":
    manifest = build_manifest()
    out = ROOT / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ manifest.json обновлён: {len(manifest['notes'])} заметок, {len(manifest['folders'])} папок")