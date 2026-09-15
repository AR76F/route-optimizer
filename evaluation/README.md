# 15-question pilot evaluation

Run one model:

```powershell
python -m evaluation.run_eval --models gpt-5.6-luna
```

Run the 100-question suite by specifying the suite file:

```powershell
python -m evaluation.run_eval --suite evaluation/gold_standard_100.jsonl --models gpt-5.6-luna --output evaluation/reports/pilot_100_luna.json
```

The 100-case suite contains knowledge, software, policy, warranty, dispatch,
technician, Ottawa/customer, and stress cases based on the current knowledge
base. Dispatch cases evaluate coordinator preparation and technician selection;
priority-code decisions remain outside this chatbot suite.

Compare models:

```powershell
python -m evaluation.run_eval --models gpt-5.6-luna gpt-5.6-terra gpt-5.6-sol --output evaluation/reports/pilot.json
```

Stop with `Ctrl+C`, then resume with the same command plus `--resume`.
Results are checkpointed after every case. Each test can define required
sources and acceptable overlapping sources with `allowed_sources`; only the
required sources affect recall, while both sets count as relevant for
contextual precision. Tests may also define `forbidden_terms` for behavior
that must not appear in an answer. The scorer measures source retrieval,
required-term coverage, answer score, latency, forbidden-content compliance,
and failures.
