"""Render summary dict as a markdown report."""
from __future__ import annotations

from datetime import datetime, timezone


def _bar(value: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return ""
    filled = int(round(width * value / total))
    return "█" * filled + "·" * (width - filled)


def _table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(out)


def render(summary: dict) -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    scrape = summary.get("scrape", {})
    apps = summary.get("applications", {})

    lines: list[str] = []
    lines.append(f"# career-scan analytics — {today}")
    lines.append("")
    lines.append(f"_Generated {summary.get('generated_at', '')}_")
    lines.append("")

    # Scrape funnel
    lines.append("## Scrape funnel")
    lines.append("")
    lines.append(f"- **Total jobs tracked**: {scrape.get('total', 0)}")
    lines.append(f"- **Added in last 24 h**: {scrape.get('added_24h', 0)}")
    lines.append(f"- **Added in last 7 d**: {scrape.get('added_7d', 0)}")
    lines.append("")

    by_source = scrape.get("by_source", {})
    if by_source:
        total_src = sum(by_source.values())
        lines.append("### By source")
        lines.append("")
        rows = [
            [src, count, f"{count / total_src:.0%}", _bar(count, total_src)]
            for src, count in by_source.items()
        ]
        lines.append(_table(["Source", "Jobs", "Share", ""], rows))
        lines.append("")

    top_companies = scrape.get("top_companies") or []
    if top_companies:
        lines.append("### Top hiring companies")
        lines.append("")
        lines.append(_table(["Company", "Jobs"], [[c, n] for c, n in top_companies]))
        lines.append("")

    # Application funnel
    lines.append("## Application funnel")
    lines.append("")
    lines.append(f"- **Total applications tracked**: {apps.get('total', 0)}")
    lines.append(f"- **Submitted in last 24 h**: {apps.get('submitted_24h', 0)}")
    lines.append(f"- **Submitted in last 7 d**: {apps.get('submitted_7d', 0)}")
    rate = apps.get("response_rate")
    if rate is not None:
        lines.append(f"- **Response rate (responded+rejected / submitted)**: {rate:.0%}")
    mts = apps.get("median_tailor_to_submit_hours")
    if mts is not None:
        lines.append(f"- **Median tailor → submit**: {mts:.1f} h")
    msr = apps.get("median_submit_to_response_hours")
    if msr is not None:
        lines.append(f"- **Median submit → response**: {msr:.1f} h")
    lines.append("")

    by_state = apps.get("by_state", {})
    if by_state:
        total_st = sum(by_state.values())
        order = ["queued", "jd_fetched", "tailored", "submitted", "responded", "rejected", "skipped", "error"]
        sorted_states = [s for s in order if s in by_state] + [s for s in by_state if s not in order]
        lines.append("### By state")
        lines.append("")
        rows = [
            [s, by_state[s], f"{by_state[s] / total_st:.0%}", _bar(by_state[s], total_st)]
            for s in sorted_states
        ]
        lines.append(_table(["State", "Count", "Share", ""], rows))
        lines.append("")

    errors = apps.get("errors") or []
    if errors:
        lines.append("### Top error reasons")
        lines.append("")
        lines.append(_table(["Reason (truncated)", "Count"], [[r, n] for r, n in errors]))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Source: [career-scan](https://github.com/wankhede04/career-scan)_")
    return "\n".join(lines) + "\n"
