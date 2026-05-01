# Trinity Reply Ranker Trace Replay

This project is the first Train-side consumer of exported Trinity reply traces.

Purpose:

- validate that Train can load Trinity reply traces safely
- replay one bounded ranking policy against deterministic fixtures
- prepare the future optimization lane without pretending live optimization is ready
- accept fixtures generated from real Trinity trace exports plus optional Reply shadow comparisons

Rules:

1. Only mutate `projects/trinity_reply_ranker/train.py`.
2. Do not rewrite the fixture into a different contract.
3. Treat this as replay scaffolding, not live product optimization.
4. Runtime ownership remains in `trinity`.
