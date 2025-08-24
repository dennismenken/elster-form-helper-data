import os
import json
import re
from pathlib import Path

# Konfigurierbare Pfade
BASE_DIR = Path("./Formulare")
API_EXPORT_BASE = Path("./API-Server/src/data/forms")


def slugify(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"^-+|-+$", "", name)
    return name


def remove_prefix(name: str) -> str:
    return re.sub(r"^(01|99)[-_\s]*", "", name.strip(), flags=re.IGNORECASE)


def merge_json_files_in_directory(directory: Path) -> list:
    merged_data = []
    json_files = sorted(directory.glob("*.json"))
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                if isinstance(content, list):
                    merged_data.extend(content)
                else:
                    print(f"WARNUNG: Datei {json_file} enthält kein Array.")
            except json.JSONDecodeError as e:
                print(f"FEHLER beim Laden von {json_file}: {e}")
    return merged_data


def process_form_directory(form_path: Path, export_path: Path, overview_path: Path, json_overview_path: Path):
    entries = []
    for formular_dir in form_path.iterdir():
        if formular_dir.is_dir():
            merged = merge_json_files_in_directory(formular_dir)
            if merged:
                export_path.mkdir(parents=True, exist_ok=True)
                cleaned_name = remove_prefix(formular_dir.name)
                slug_name = slugify(cleaned_name)
                export_file = export_path / f"{slug_name}.json"
                with open(export_file, "w", encoding="utf-8") as f:
                    json.dump(merged, f, ensure_ascii=False, indent=2)
                print(f"Exportiert: {export_file}")
                entries.append(("hauptvordruck" in slug_name, slug_name, cleaned_name))

    # Übersichten schreiben, Hauptvordruck zuerst, Rest sortiert
    if entries:
        sorted_entries = sorted(entries, key=lambda x: (not x[0], x[1]))

        # Endpunkt-Übersicht (wie bisher)
        endpoint_lines = ["# API-Endpunkte\n"]
        for _, slug, name in sorted_entries:
            endpoint_lines.append(f"- `{slug}` ← {name}")
        overview_path.parent.mkdir(parents=True, exist_ok=True)
        with open(overview_path, "w", encoding="utf-8") as f:
            f.write("\n".join(endpoint_lines))

        # JSON-Daten Übersicht
        json_lines = ["# JSON-Daten\n"]
        for _, slug, name in sorted_entries:
            json_lines.append(f"- `{slug}.json` ← {name}")
        with open(json_overview_path, "w", encoding="utf-8") as f:
            f.write("\n".join(json_lines))


def main():
    for category_dir in BASE_DIR.iterdir():
        if category_dir.is_dir():
            category_slug = slugify(category_dir.name)
            for year_dir in category_dir.iterdir():
                if year_dir.is_dir():
                    export_path = API_EXPORT_BASE / category_slug / year_dir.name
                    overview_file = year_dir / "Endpunkt-Uebersicht.md"
                    json_overview_file = year_dir / "JSON-Daten.md"
                    process_form_directory(year_dir, export_path, overview_file, json_overview_file)


if __name__ == "__main__":
    main()
