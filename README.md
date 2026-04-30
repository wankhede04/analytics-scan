# analytics-scan

Daily analytics layer on top of [`career-scan`](https://github.com/wankhede04/career-scan):

- pulls the latest `remote_jobs.xlsx` and `applications/_state.json` from
  `career-scan@main`
- computes scrape-funnel and application-funnel metrics
- writes a markdown dashboard (`reports/latest.md`), a long-form daily report
  (`reports/<YYYY-MM-DD>.md`), and `reports/summary.json` for downstream
  tools / charts

Runs every morning at **08:00 UTC** — 30 minutes after the auto-applier in
`career-scan` finishes — via `.github/workflows/daily_report.yml`.

## What gets reported

### Scrape funnel

| Metric | Source |
|---|---|
| Total jobs ever recorded | rows in `remote_jobs.xlsx` |
| Jobs added in last 24 h / 7 d | `Date Added` column |
| Per-portal share | `Source` column |
| Top hiring companies | `Company` column |

### Application funnel

| Metric | Source |
|---|---|
| Queued / JD-fetched / Tailored / Submitted / Responded | `applications/_state.json` |
| Median time from `tailored` -> `submitted` | record `history` |
| Submit-to-response conversion rate | record state transitions |
| Top error reasons | `error` field on records |

## Local Usage

```bash
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_...   # any PAT with read access to career-scan
python -m analytics.main
```

Outputs go to `reports/`. The script is read-only with respect to
`career-scan` — it never writes back.
