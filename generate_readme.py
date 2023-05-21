import sys
from pathlib import Path
from typing import List
import re

def generate_readme(directory: Path) -> None:
    readme_lines = read_file_contents(directory / "README_HEADER.md")

    png_files = find_files(directory=directory, pattern="*.png")
    readme_lines = add_sections_to_readme(directory=directory, readme_lines=readme_lines, files=png_files)

    mmd_files = find_files(directory=directory, pattern="*.mmd")
    readme_lines = add_sections_to_readme(directory=directory, readme_lines=readme_lines, files=mmd_files)

    write_readme(directory=directory, readme_lines=readme_lines)

def read_file_contents(file_path: Path) -> List[str]:
    try:
        with open(file_path, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        return []

def find_files(directory: Path, pattern: str) -> List[Path]:
    return list(directory.rglob(pattern))

def add_sections_to_readme(directory: Path, readme_lines: List[str], files: List[Path]) -> List[str]:
    sections = {}
    for path in files:
        folder_name = path.parent.name
        semantic_version = extract_semantic_version(path.name)
        if "venv" in str(path):
            continue
        if folder_name in sections:
            sections[folder_name].append((semantic_version, path))
        else:
            sections[folder_name] = [(semantic_version, path)]

    sorted_sections = sorted(sections.items())

    for folder_name, versions in sorted_sections:
        section_lines = []
        for semantic_version, path in sorted(versions, key=lambda x: x[0].split(".")):
            section_lines.append(f"## {semantic_version}\n")
            mmd_contents = get_file_contents(path.with_suffix(".mmd"))
            if mmd_contents:
                section_lines.append("```text\n")
                section_lines.append(mmd_contents)
                section_lines.append("```\n")
            section_lines.append(f"![]({path.relative_to(directory)})\n")
        if section_lines:
            readme_lines.append(f"## {folder_name}\n")
            readme_lines.extend(section_lines)

    return readme_lines

def extract_semantic_version(filename: str) -> str:
    version_match = re.search(r"(\d+\.\d+\.\d+)", filename)
    if version_match:
        return version_match.group(1)
    return ""

def get_file_contents(file_path: Path) -> str:
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""

def write_readme(directory: Path, readme_lines: List[str]) -> None:
    with open(directory / "README.md", "w") as readme_file:
        readme_file.writelines(readme_lines)

if __name__ == "__main__":
    generate_readme(Path.cwd())
