import sys
import subprocess
import requests
from dataclasses import dataclass
from typing import List
from pathlib import Path

@dataclass
class Release:
    version: str


def main():
    if len(sys.argv) < 2:
        print("Please provide the name of the library as a command line argument.")
        sys.exit(1)

    library_name = sys.argv[1]
    show_every_n_minor_versions = int(input("Enter the value for show_every_n_minor_versions: "))

    data: dict = fetch_library_data(library_name=library_name)
    releases = parse_releases(data=data)
    sampled_releases = sample_releases(releases=releases, show_every_n_minor_versions=show_every_n_minor_versions)

    for i, release in enumerate(sampled_releases):
        generate_dependency_diagram(library_name=library_name, version=release.version, index=i)


def generate_dependency_diagram(library_name: str, version: str, index: int):
    outdir = Path.cwd() / library_name
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        venv_dir = install_library(library_name=library_name, version=version, outdir=outdir)
    except subprocess.CalledProcessError as err:
        print(f"Failed to install library: {library_name}=={version}")
        print(err)
        return

    generate_mermaid_file(library_name=library_name, version=version, outdir=outdir, venv_dir=venv_dir, index=index)

    try:
        generate_image(library_name=library_name, version=version, outdir=outdir, venv_dir=venv_dir, index=index)
    except subprocess.CalledProcessError as err:
        print(f"Failed to generate image for library: {library_name}=={version}")
        print(err)
        return


def install_library(library_name: str, version: str, outdir: Path):
    venv_dir = outdir / "venvs" / f"{library_name}-{version}-env"
    subprocess.run(["python", "-m", "venv", str(venv_dir)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([f"{venv_dir}/bin/pip", "install", f"{library_name}=={version}", "pipdeptree", "graphviz"], stdout=subprocess.DEVNULL, check=True)
    return venv_dir


def generate_mermaid_diagram(library_name: str, version: str, venv_dir: Path) -> str:
    output = subprocess.run([f"{venv_dir}/bin/pipdeptree"], check=True, capture_output=True)
    return output.stdout.decode('utf-8')


def generate_mermaid_file(library_name: str, version: str, outdir: Path, venv_dir: Path, index: int):
    mermaid_diagram = generate_mermaid_diagram(library_name=library_name, version=version, venv_dir=venv_dir)
    outfile_fpath = outdir / f"{index}_{library_name}-{version}.mmd"
    outfile_fpath.write_text(mermaid_diagram)


def generate_image(library_name: str, version: str, outdir: Path, venv_dir: Path, index: int):
    output = subprocess.run([f"{venv_dir}/bin/pipdeptree", "--graph-output=png", f"--packages={library_name}"], check=True, capture_output=True)
    outfile_fpath = outdir / f"{index}_{library_name}-{version}.png"
    outfile_fpath.write_bytes(output.stdout)


def sample_releases(releases: List[Release], show_every_n_minor_versions: int):
    sampled_releases = releases[::show_every_n_minor_versions]
    return sampled_releases


def parse_releases(data):
    releases = []
    for version, release_data in data['releases'].items():
        if len(release_data) == 0:
            continue
        release = Release(version=version)
        releases.append(release)
    return releases


def fetch_library_data(library_name: str):
    response = requests.get(f"https://pypi.org/pypi/{library_name}/json")
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data for library: {library_name}")


if __name__ == "__main__":
    main()
