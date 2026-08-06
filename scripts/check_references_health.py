#!/usr/bin/env python3
"""Pantalone references 健康检查脚本

只读检查，不修改任何文件。
检查内容：
1. 入口文件中的 references/*.md 引用是否存在
2. subagents/ 清单与 router.md/SKILL.md 覆盖一致性
3. Newtown 是否只出现在 legacy alias 语境
4. templates/ 根目录是否有 .bak
5. scripts/amadeus/ 根目录是否有旧训练脚本

用法：
    python3 check_references_health.py [--json] [--quiet]
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# 路径配置
PANTALONE_ROOT = Path(__file__).parent.parent
REFERENCES_DIR = PANTALONE_ROOT / "references"
SUBAGENTS_DIR = PANTALONE_ROOT / "subagents"
TEMPLATES_DIR = PANTALONE_ROOT / "templates"
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
INSTALLED_SCRIPTS_DIR = HERMES_HOME / "scripts" / "amadeus"


def find_ancestor_scripts_dir(start: Path) -> Optional[Path]:
    """Find a host scripts/amadeus directory without assuming checkout depth."""
    for ancestor in (start.resolve(), *start.resolve().parents):
        candidate = ancestor / "scripts" / "amadeus"
        if candidate.is_dir():
            return candidate
    return None


REPOSITORY_SCRIPTS_DIR = find_ancestor_scripts_dir(PANTALONE_ROOT)
SCRIPTS_DIR = REPOSITORY_SCRIPTS_DIR

# 入口文件
ENTRY_FILES = [
    "SKILL.md",
    "router.md",
    "workflow_v4_unified.md",
    "SOUL.md",
]

# 旧训练脚本模式
OLD_TRAIN_PATTERNS = [
    "train_v3*.py",
    "train_v4*.py",
    "train_v41*.py",
    "train_v44*.py",
    "train_v45*.py",
    "train_v46*.py",
]


def check_references_exist() -> Dict:
    """检查入口文件中的 references/*.md 引用是否存在"""
    missing = []
    found = []
    entry_refs = {}

    for entry_file in ENTRY_FILES:
        entry_path = PANTALONE_ROOT / entry_file
        if not entry_path.exists():
            continue

        content = entry_path.read_text(encoding="utf-8")
        # 匹配 references/*.md 引用
        refs = re.findall(r"references/[\w.-]+\.md", content)
        entry_refs[entry_file] = list(set(refs))

        for ref in set(refs):
            ref_path = PANTALONE_ROOT / ref
            if ref_path.exists():
                found.append({"file": entry_file, "ref": ref, "status": "ok"})
            else:
                missing.append({"file": entry_file, "ref": ref, "status": "missing"})

    return {
        "total_refs": len(found) + len(missing),
        "found": len(found),
        "missing": len(missing),
        "missing_details": missing,
        "by_entry": entry_refs,
    }


def check_subagents_coverage() -> Dict:
    """检查 subagents/ 清单与 router.md/SKILL.md 覆盖一致性"""
    # 获取实际 subagent 文件
    actual_files = set()
    if SUBAGENTS_DIR.exists():
        for f in SUBAGENTS_DIR.iterdir():
            if f.is_file() and f.suffix == ".md":
                actual_files.add(f.name)

    # 获取 router.md 中引用的 subagent
    router_refs = set()
    router_path = PANTALONE_ROOT / "router.md"
    if router_path.exists():
        content = router_path.read_text(encoding="utf-8")
        refs = re.findall(r"subagents/([\w.-]+\.md)", content)
        router_refs = set(refs)

    # 获取 SKILL.md 中引用的 subagent
    skill_refs = set()
    skill_path = PANTALONE_ROOT / "SKILL.md"
    if skill_path.exists():
        content = skill_path.read_text(encoding="utf-8")
        refs = re.findall(r"subagents/([\w.-]+\.md)", content)
        skill_refs = set(refs)

    # 计算差异
    only_in_dir = actual_files - router_refs - skill_refs
    only_in_router = router_refs - actual_files
    only_in_skill = skill_refs - actual_files

    return {
        "actual_files": sorted(actual_files),
        "router_refs": sorted(router_refs),
        "skill_refs": sorted(skill_refs),
        "only_in_dir": sorted(only_in_dir),
        "only_in_router": sorted(only_in_router),
        "only_in_skill": sorted(only_in_skill),
        "consistent": len(only_in_dir) == 0 and len(only_in_router) == 0 and len(only_in_skill) == 0,
    }


def check_newtown_usage() -> Dict:
    """检查 Newtown 是否只出现在 legacy alias 语境"""
    results = []
    search_files = list(PANTALONE_ROOT.glob("*.md")) + list(PANTALONE_ROOT.glob("*.py"))

    # 排除 backups 和 archive
    exclude_dirs = {"backups", "archive", ".git"}

    for f in search_files:
        if any(d in str(f) for d in exclude_dirs):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            for i, line in enumerate(content.split("\n"), 1):
                if "Newtown" in line or "newtown" in line:
                    # 判断是否为 legacy alias 语境
                    is_legacy = any(
                        kw in line.lower()
                        for kw in [
                            "legacy", "alias", "旧名", "兼容", "重命名",
                            # 脚本功能描述/文档说明中的安全引用
                            "命名规范", "命名检查", "命名验证",
                            "检查入口", "检查脚本", "检查工具",
                            "health.py", "check_references",
                        ]
                    )
                    results.append({
                        "file": str(f.relative_to(PANTALONE_ROOT)),
                        "line": i,
                        "content": line.strip()[:100],
                        "is_legacy_context": is_legacy,
                    })
        except Exception:
            pass

    non_legacy = [r for r in results if not r["is_legacy_context"]]

    return {
        "total_occurrences": len(results),
        "legacy_context": len(results) - len(non_legacy),
        "non_legacy": len(non_legacy),
        "non_legacy_details": non_legacy,
    }


def check_templates_bak() -> Dict:
    """检查 templates/ 根目录是否有 .bak"""
    bak_files = []
    if TEMPLATES_DIR.exists():
        for f in TEMPLATES_DIR.iterdir():
            if f.is_file() and f.suffix == ".bak":
                bak_files.append(f.name)

    return {
        "count": len(bak_files),
        "files": bak_files,
        "clean": len(bak_files) == 0,
    }


def check_old_train_scripts() -> Dict:
    """检查 scripts/amadeus/ 根目录是否有旧训练脚本"""
    old_scripts = []
    current_scripts = []

    if SCRIPTS_DIR is not None and SCRIPTS_DIR.exists():
        import glob
        for pattern in OLD_TRAIN_PATTERNS:
            for f in SCRIPTS_DIR.glob(pattern):
                old_scripts.append(f.name)

        for f in SCRIPTS_DIR.glob("train_v5*.py"):
            current_scripts.append(f.name)

    return {
        "old_count": len(old_scripts),
        "old_files": sorted(old_scripts),
        "current_count": len(current_scripts),
        "current_files": sorted(current_scripts),
        "clean": len(old_scripts) == 0,
    }


CREDENTIAL_PATTERNS = [
    re.compile(r'''["']sk-[A-Za-z0-9_-]{20,}["']'''),
    re.compile(
        r'''(?i)(?:^|[^A-Za-z0-9_])(?:token|api[_-]?key|secret)\b'''
        r'''\s*[:=]\s*[`"']?[A-Za-z0-9_./+=-]{16,}[`"']?'''
    ),
]
CREDENTIAL_SUFFIXES = {
    ".cfg", ".conf", ".env", ".ini", ".json", ".md", ".py", ".sh",
    ".toml", ".txt", ".yaml", ".yml",
}
CREDENTIAL_EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", "backups", "catboost_info"}


def check_credentials() -> Dict:
    """检查疑似硬编码密钥，不返回命中内容"""
    findings = []
    scan_roots = [("pantalone", PANTALONE_ROOT)]
    if SCRIPTS_DIR is not None and SCRIPTS_DIR.exists():
        scan_roots.append(("amadeus", SCRIPTS_DIR))

    for label, base in scan_roots:
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in CREDENTIAL_SUFFIXES:
                continue
            relative = path.relative_to(base)
            if CREDENTIAL_EXCLUDE_DIRS.intersection(relative.parts):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for line_number, line in enumerate(lines, 1):
                if any(pattern.search(line) for pattern in CREDENTIAL_PATTERNS):
                    findings.append({
                        "file": f"{label}/{relative}",
                        "line": line_number,
                    })

    return {
        "total": len(findings),
        "findings": findings,
        "clean": len(findings) == 0,
    }


def generate_summary(checks: Dict) -> str:
    """生成人类可读摘要"""
    lines = []
    lines.append("=" * 60)
    lines.append("Pantalone References 健康检查报告")
    lines.append("=" * 60)
    lines.append("")

    # 1. References 引用
    ref_check = checks["references"]
    status = "✅" if ref_check["missing"] == 0 else "❌"
    lines.append(f"1. 入口引用完整性 {status}")
    lines.append(f"   总引用: {ref_check['total_refs']}, 存在: {ref_check['found']}, 缺失: {ref_check['missing']}")
    if ref_check["missing_details"]:
        for m in ref_check["missing_details"]:
            lines.append(f"   ❌ {m['file']} → {m['ref']}")
    lines.append("")

    # 2. Subagents 覆盖
    sub_check = checks["subagents"]
    status = "✅" if sub_check["consistent"] else "⚠️"
    lines.append(f"2. Subagent 清单一致性 {status}")
    lines.append(f"   实际文件: {len(sub_check['actual_files'])}, router 引用: {len(sub_check['router_refs'])}, SKILL 引用: {len(sub_check['skill_refs'])}")
    if sub_check["only_in_dir"]:
        lines.append(f"   ⚠️ 目录有但未引用: {', '.join(sub_check['only_in_dir'])}")
    if sub_check["only_in_router"]:
        lines.append(f"   ❌ router 引用但不存在: {', '.join(sub_check['only_in_router'])}")
    if sub_check["only_in_skill"]:
        lines.append(f"   ❌ SKILL 引用但不存在: {', '.join(sub_check['only_in_skill'])}")
    lines.append("")

    # 3. Newtown 使用
    nt_check = checks["newtown"]
    status = "✅" if nt_check["non_legacy"] == 0 else "⚠️"
    lines.append(f"3. Newtown 命名规范 {status}")
    lines.append(f"   总出现: {nt_check['total_occurrences']}, legacy 语境: {nt_check['legacy_context']}, 非 legacy: {nt_check['non_legacy']}")
    if nt_check["non_legacy_details"]:
        for d in nt_check["non_legacy_details"][:5]:
            lines.append(f"   ⚠️ {d['file']}:{d['line']} → {d['content'][:60]}")
    lines.append("")

    # 4. Templates .bak
    bak_check = checks["templates_bak"]
    status = "✅" if bak_check["clean"] else "⚠️"
    lines.append(f"4. Templates .bak 清理 {status}")
    lines.append(f"   根目录 .bak 文件: {bak_check['count']}")
    if bak_check["files"]:
        lines.append(f"   文件: {', '.join(bak_check['files'])}")
    lines.append("")

    # 5. 旧训练脚本
    train_check = checks["old_train_scripts"]
    status = "✅" if train_check["clean"] else "⚠️"
    lines.append(f"5. 旧训练脚本清理 {status}")
    lines.append(f"   旧脚本: {train_check['old_count']}, 当前版本: {train_check['current_count']}")
    if train_check["old_files"]:
        lines.append(f"   旧脚本: {', '.join(train_check['old_files'])}")
    lines.append("")

    # 6. 密钥字面量
    credential_check = checks["credentials"]
    status = "✅" if credential_check["clean"] else "⚠️"
    lines.append(f"6. 密钥硬编码扫描 {status}")
    lines.append(f"   疑似硬编码: {credential_check['total']} 处")
    for finding in credential_check["findings"]:
        lines.append(f"   ⚠️ {finding['file']}:{finding['line']}")
    lines.append("")

    # 总结
    lines.append("=" * 60)
    all_ok = (
        ref_check["missing"] == 0
        and sub_check["consistent"]
        and nt_check["non_legacy"] == 0
        and bak_check["clean"]
        and train_check["clean"]
        and credential_check["clean"]
    )
    if all_ok:
        lines.append("✅ 所列静态检查通过")
        lines.append("未覆盖：宿主外部能力可用性、外部HTTP响应、Schema语义、真实Hermes运行态E2E")
    else:
        lines.append("⚠️ 发现问题，请检查上述详情")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pantalone references 健康检查")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--quiet", action="store_true", help="只输出摘要行")
    args = parser.parse_args()

    checks = {
        "references": check_references_exist(),
        "subagents": check_subagents_coverage(),
        "newtown": check_newtown_usage(),
        "templates_bak": check_templates_bak(),
        "old_train_scripts": check_old_train_scripts(),
        "credentials": check_credentials(),
    }

    if args.json:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        summary = generate_summary(checks)
        if args.quiet:
            # 只输出关键状态行
            for line in summary.split("\n"):
                if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "✅", "⚠️", "❌", "未覆盖：")):
                    print(line)
        else:
            print(summary)


if __name__ == "__main__":
    main()
