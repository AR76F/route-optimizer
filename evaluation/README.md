# Service Assistant Evaluation Loop

The evaluator runs the assistant directly; it does not change the Streamlit
interface. JSON reports contain answers, retrieved chunks, timing, model names,
and automated scores.

## 1. Check the repository

Run these commands from the repository root:

```powershell
git status --short
git diff --stat
```

## 2. Install or verify dependencies

```powershell
python -m pip install -r requirements.txt
```

The environment must also have `OPENAI_API_KEY` configured.

## 3. Run the 15-question pilot

```powershell
python -m evaluation.run_eval `
  --suite evaluation/gold_standard.jsonl `
  --models gpt-5.6-luna `
  --output evaluation/reports/pilot_v4.json `
  --timeout 90 `
  --retries 1
```

Compare all three models:

```powershell
python -m evaluation.run_eval `
  --suite evaluation/gold_standard.jsonl `
  --models gpt-5.6-luna gpt-5.6-terra gpt-5.6-sol `
  --output evaluation/reports/pilot_models_v2.json `
  --timeout 90 `
  --retries 1
```

## 4. Run the 100-question benchmark

```powershell
python -m evaluation.run_eval `
  --suite evaluation/gold_standard_100.jsonl `
  --models gpt-5.6-luna gpt-5.6-terra gpt-5.6-sol `
  --output evaluation/reports/pilot_100_models.json `
  --timeout 90 `
  --retries 1
```

The 100-case suite covers BMS, FieldAware, Clover, policies, warranties,
dispatch, technician selection, Ottawa/customer cases, French questions, and
stress cases. Dispatch tests evaluate coordinator preparation and technician
selection; priority-code decisions remain in separate prioritization-engine
tests. The runtime is around 3-4 minutes

## 5. Stop and resume safely

Stop a running test with `Ctrl + C`. Results are checkpointed after each case.
Resume using the exact same suite, model list, and output path:

```powershell
python -m evaluation.run_eval `
  --suite evaluation/gold_standard_100.jsonl `
  --models gpt-5.6-luna gpt-5.6-terra gpt-5.6-sol `
  --output evaluation/reports/pilot_100_models.json `
  --timeout 90 `
  --retries 1 `
  --resume
```

Do not use `--resume` after changing the suite or scoring rules. Use a new
report filename instead.

## 6. Inspect a report

```powershell
Get-ChildItem -LiteralPath .\evaluation\reports -Filter *.json -File |
  Sort-Object LastWriteTime
```

```powershell
$report = Get-Content -Raw .\evaluation\reports\pilot_100_models.json |
  ConvertFrom-Json
$report.models.psobject.Properties | ForEach-Object {
  Write-Output "MODEL: $($_.Name)"
  $_.Value.summary | ConvertTo-Json
}
```

Inspect failures:

```powershell
$report.models.psobject.Properties | ForEach-Object {
  $_.Value.results |
    Where-Object { $_.error } |
    Select-Object id, error
}
```

## 7. Clean generated reports

Delete generated JSON reports while keeping the evaluator and test suites:

```powershell
Get-ChildItem -LiteralPath .\evaluation\reports -Filter *.json -File |
  Remove-Item -Force
```

Remove generated Python cache files if needed:

```powershell
if (Test-Path -LiteralPath .\evaluation\__pycache__) {
  Remove-Item -LiteralPath .\evaluation\__pycache__ -Recurse -Force
}
```

## 8. Review and save evaluation changes

```powershell
git status --short
git diff -- service_assistant.py evaluation\run_eval.py evaluation\README.md
git add service_assistant.py evaluation
git commit -m "Add service assistant evaluation framework"
```

Generated reports should generally not be committed because they contain
internal knowledge-base excerpts and can be large. Add
`evaluation/reports/*.json` to `.gitignore` if reports should remain local.

The scorer supports required sources, acceptable overlapping sources through
`allowed_sources`, required terms, forbidden terms, contextual precision,
required-source recall, answer score, latency, and failure counts. It is a
transparent pilot scorer and should eventually be complemented by independent
human or LLM judging.
