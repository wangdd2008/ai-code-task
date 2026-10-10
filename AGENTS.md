## Agent skills

### Task workspace

这是一个 AI 任务工程。所有任务都在 `src/` 目录下创建独立文件夹（`src/<NN>-<task-name>/`），其中 `NN` 为两位数字编号。每个任务的过程产出（spec、issues、代码、文档等）必须存放在对应的任务目录内，不得污染其他目录。是否创建新任务由用户决定。

### Issue tracker

Issues live as files under `.scratch/` in this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

Using the five canonical roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
