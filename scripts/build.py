#!/usr/bin/env python3
"""Compile IP rules and verify that the binary contains exactly the source ranges."""
import hashlib
import html
import ipaddress
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "direct-ip.json"
OUTPUT = ROOT / "dist"


def networks(document):
    if document.get("version") != 1 or not document.get("rules"):
        raise ValueError("Expected version 1 and a nonempty rules array")
    result = []
    for rule in document["rules"]:
        if set(rule) != {"ip_cidr"}:
            raise ValueError("Each rule must contain only ip_cidr")
        # sing-box serializes a one-element array as a string when decompiling.
        values = rule["ip_cidr"]
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list) or not values:
            raise ValueError("ip_cidr must contain at least one CIDR")
        result.extend(ipaddress.ip_network(value, strict=True) for value in values)
    return tuple(
        str(network)
        for version in (4, 6)
        for network in ipaddress.collapse_addresses(n for n in result if n.version == version)
    )


def main():
    expected = networks(json.loads(SOURCE.read_text()))
    compiler = os.environ.get("SING_BOX", "sing-box")
    with tempfile.TemporaryDirectory(prefix="vilaxvpn-rules-") as temporary:
        binary = Path(temporary) / "direct-ip.srs"
        decoded = Path(temporary) / "decoded.json"
        subprocess.run([compiler, "rule-set", "compile", "--output", str(binary), str(SOURCE)], check=True)
        if binary.read_bytes()[:4] != b"SRS\x01":
            raise ValueError("Expected an SRS version 1 binary")
        subprocess.run([compiler, "rule-set", "decompile", "--output", str(decoded), str(binary)], check=True)
        if networks(json.loads(decoded.read_text())) != expected:
            raise ValueError("Compiled rules differ from the source")
        OUTPUT.mkdir(exist_ok=True)
        shutil.copyfile(binary, OUTPUT / binary.name)
    shutil.copyfile(SOURCE, OUTPUT / SOURCE.name)
    (OUTPUT / ".nojekyll").touch()
    items = "".join(f"<li><code>{html.escape(cidr)}</code></li>" for cidr in expected)
    (OUTPUT / "index.html").write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>VilaxVPN 直连规则</title><h1>VilaxVPN 直连规则</h1>'
        '<p><a href="direct-ip.srs">下载 direct-ip.srs</a> · '
        '<a href="direct-ip.json">查看 JSON 源文件</a> · '
        '<a href="https://github.com/kkxiaoa/vilaxvpn-rules/edit/main/direct-ip.json">修改网段</a></p>'
        '<p>在客户端添加 .srs 下载地址，动作选择“直连”，关闭“反选”。</p>'
        f'<ul>{items}</ul></html>\n'
    )
    checksums = "".join(
        f"{hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest()}  {name}\n"
        for name in ("direct-ip.srs", "direct-ip.json")
    )
    (OUTPUT / "SHA256SUMS").write_text(checksums)
    print("Verified rules:", ", ".join(expected))
    print(checksums, end="")


if __name__ == "__main__":
    main()
