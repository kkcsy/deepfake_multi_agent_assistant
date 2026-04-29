from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".tex",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".log",
    ".bib",
}


def read_text(path: Path, max_chars: int = 30000) -> str:
    if not path.exists():
        return f"[文件不存在] {path}"

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(path, max_chars=max_chars)

    if suffix not in TEXT_EXTENSIONS:
        return f"[暂不支持该文件类型，仅记录文件名] {path.name}"

    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            text = path.read_text(encoding=encoding, errors="ignore")
            break
        except Exception:
            text = ""
    else:
        return f"[读取失败] {path}"

    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[内容过长，已截断]\n"

    return f"\n\n===== 文件：{path.name} =====\n{text}"


def read_pdf(path: Path, max_chars: int = 30000) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return f"[缺少 pypdf，无法读取 PDF] {path.name}"

    try:
        reader = PdfReader(str(path))
        pages = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(f"\n--- Page {idx + 1} ---\n{text}")
        joined = "\n".join(pages)
        if len(joined) > max_chars:
            joined = joined[:max_chars] + "\n\n[PDF 内容过长，已截断]\n"
        return f"\n\n===== PDF：{path.name} =====\n{joined}"
    except Exception as exc:
        return f"[PDF 读取失败] {path.name}: {exc}"


def read_files(paths: Iterable[str], max_chars_each: int = 30000) -> str:
    chunks: List[str] = []
    for raw_path in paths:
        chunks.append(read_text(Path(raw_path), max_chars=max_chars_each))
    return "\n".join(chunks)


def read_task(task: str = "", task_file: str = "") -> str:
    if task:
        return task.strip()
    if task_file:
        return Path(task_file).read_text(encoding="utf-8", errors="ignore").strip()
    raise ValueError("必须提供 --task 或 --task-file。")


def preview_csv(path: Path, max_rows: int = 10) -> str:
    if not path.exists():
        return f"[CSV 文件不存在] {path}"
    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = []
            for i, row in enumerate(reader):
                if i >= max_rows:
                    break
                rows.append(row)
        lines = [f"===== CSV 预览：{path.name} =====", f"字段：{headers}"]
        for idx, row in enumerate(rows, start=1):
            lines.append(f"{idx}. {row}")
        return "\n".join(lines)
    except Exception as exc:
        return f"[CSV 预览失败] {path.name}: {exc}"
