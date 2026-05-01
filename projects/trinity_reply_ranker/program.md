# {trinity} {reply} Ranker Trace Replay

This project is the first `{train}`-side consumer of exported `{trinity}` `{reply}` traces.

Purpose:

- validate that `{train}` can load `{trinity}` `{reply}` traces safely
- replay one bounded ranking policy against deterministic fixtures
- prepare the future optimization lane without pretending live optimization is ready
- accept fixtures generated from real `{trinity}` trace exports plus optional `{reply}` shadow comparisons

Rules:

1. Only mutate `projects/trinity_reply_ranker/train.py`.
2. Do not rewrite the fixture into a different contract.
3. Treat this as replay scaffolding, not live product optimization.
4. Runtime ownership remains in `trinity`.
