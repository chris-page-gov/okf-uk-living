#!/usr/bin/env python3
"""Create body-free link receipts for one staged population pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_source_links import verify
from build_okf_bundle import ROOT
from check_domain_registers import load_registers, register_sources


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True)
    parser.add_argument("--checked-at", required=True)
    args = parser.parse_args()
    selected = [item for item in load_registers()[0] if item[1].get("pack_id") == args.pack]
    if not selected:
        print(f"no domain registers found for {args.pack}")
        return 1
    receipt_roots = {str(register.get("link_receipts")) for _, register in selected}
    if len(receipt_roots) != 1:
        print(f"{args.pack} must declare one receipt directory")
        return 1
    output = ROOT / receipt_roots.pop()
    output.mkdir(parents=True, exist_ok=True)
    sources = [source for _, register in selected for source in register_sources(register)]
    failures = 0
    for source in sources:
        receipt = verify(str(source["id"]), str(source["resource"]), args.checked_at)
        if receipt["result"] not in {"active", "redirected-active"}:
            failures += 1
        (output / f"{source['id']}.json").write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"{source['id']}: {receipt['result']} ({receipt['status_code']})")
    print(f"wrote {len(sources)} body-free receipts; {failures} require browser review")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
