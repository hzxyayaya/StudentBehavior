from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DefaultPaths:
    input_dir: Path
    output_dir: Path
    output_csv: Path
    output_warning_json: Path


def build_default_paths(repo_root: Path) -> DefaultPaths:
    output_dir = repo_root / "artifacts" / "semester_features"
    return DefaultPaths(
        input_dir=repo_root / "数据集及类型",
        output_dir=output_dir,
        output_csv=output_dir / "v1_semester_features.csv",
        output_warning_json=output_dir / "v1_warnings.json",
    )
