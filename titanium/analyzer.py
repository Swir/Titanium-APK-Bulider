from __future__ import annotations

import html.parser
import re
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str


class _AssetParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []
        self.manifest: str | None = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        for key in ("src", "href", "poster"):
            value = data.get(key)
            if value:
                self.refs.append(value)
        if tag.lower() == "link" and data.get("rel", "").lower() == "manifest":
            self.manifest = data.get("href")


def _is_remote(value: str) -> bool:
    return value.startswith(("http://", "https://", "data:", "blob:", "mailto:", "tel:", "#", "javascript:"))


def _safe_zip_members(archive: Path) -> list[zipfile.ZipInfo]:
    with zipfile.ZipFile(archive) as z:
        members = z.infolist()
        for member in members:
            p = Path(member.filename)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError(f"Unsafe ZIP path: {member.filename}")
        return members


def _find_project_root(root: Path) -> Path | None:
    direct = root / "index.html"
    if direct.is_file():
        return root
    hits = list(root.rglob("index.html"))
    return hits[0].parent if len(hits) == 1 else None


def analyze_source(source_type: str, source: str) -> list[Finding]:
    source_type = source_type.strip()
    source = source.strip()
    findings: list[Finding] = []

    if source_type == "URL":
        parsed = urlparse(source)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return [Finding("ERROR", "URL must be a valid http:// or https:// address.")]
        if parsed.scheme == "http":
            findings.append(Finding("WARNING", "The app uses plain HTTP. Prefer HTTPS for production builds."))
        findings.append(Finding("OK", f"Remote web app host: {parsed.netloc}"))
        return findings

    src = Path(source)
    if source_type == "Folder":
        if not src.is_dir():
            return [Finding("ERROR", "Selected HTML folder does not exist.")]
        return _analyze_tree(src)

    if source_type == "ZIP":
        if not src.is_file() or src.suffix.lower() != ".zip":
            return [Finding("ERROR", "Select a valid ZIP archive.")]
        try:
            members = _safe_zip_members(src)
        except (ValueError, zipfile.BadZipFile) as exc:
            return [Finding("ERROR", str(exc))]
        total = sum(x.file_size for x in members)
        if total > 500 * 1024 * 1024:
            findings.append(Finding("WARNING", f"Uncompressed web project is large ({total / 1024 / 1024:.1f} MB)."))
        with tempfile.TemporaryDirectory(prefix="titanium-analyze-") as td:
            with zipfile.ZipFile(src) as z:
                z.extractall(td)
            findings.extend(_analyze_tree(Path(td)))
        return findings

    return [Finding("ERROR", f"Unsupported source type: {source_type}")]


def _analyze_tree(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    project = _find_project_root(root)
    if not project:
        return [Finding("ERROR", "Project must contain exactly one discoverable index.html entry point.")]

    index = project / "index.html"
    try:
        text = index.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding("ERROR", f"Cannot read index.html: {exc}")]

    parser = _AssetParser()
    try:
        parser.feed(text)
    except Exception as exc:
        findings.append(Finding("WARNING", f"HTML parser reported a problem: {exc}"))

    files = [p for p in project.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    findings.append(Finding("OK", f"Found index.html and {len(files)} project files ({total / 1024 / 1024:.1f} MB)."))

    missing: list[str] = []
    insecure: list[str] = []
    file_urls: list[str] = []
    for ref in parser.refs:
        clean = ref.split("?", 1)[0].split("#", 1)[0].strip()
        if not clean:
            continue
        if clean.startswith("http://"):
            insecure.append(clean)
            continue
        if clean.startswith("file://"):
            file_urls.append(clean)
            continue
        if _is_remote(clean) or clean.startswith("/"):
            continue
        candidate = (project / clean).resolve()
        try:
            candidate.relative_to(project.resolve())
        except ValueError:
            missing.append(ref)
            continue
        if not candidate.exists():
            missing.append(ref)

    if missing:
        preview = ", ".join(missing[:5])
        extra = f" (+{len(missing)-5} more)" if len(missing) > 5 else ""
        findings.append(Finding("ERROR", f"Missing or unsafe local assets: {preview}{extra}"))
    if insecure:
        findings.append(Finding("WARNING", f"Found {len(insecure)} plain-HTTP asset reference(s)."))
    if file_urls:
        findings.append(Finding("WARNING", f"Found {len(file_urls)} file:// reference(s); these may not work inside Android WebView."))

    manifest_path = project / parser.manifest if parser.manifest and not _is_remote(parser.manifest) else project / "manifest.json"
    if manifest_path.is_file():
        findings.append(Finding("OK", f"PWA manifest detected: {manifest_path.name}"))
    else:
        findings.append(Finding("INFO", "No local PWA manifest detected. This is optional."))

    if re.search(r"serviceWorker\s*\.\s*register|navigator\.serviceWorker", text, re.I):
        findings.append(Finding("INFO", "Service worker usage detected; test offline behavior in the generated app."))

    if not any(f.severity == "ERROR" for f in findings):
        findings.append(Finding("READY", "Project preflight passed. Titanium can proceed to build."))
    return findings
