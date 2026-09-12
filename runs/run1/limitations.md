# Limitations

- Model version/build identifier, exact system prompt, exact developer prompt, temperature, `top_p`, maximum output tokens, and memory access were `UNAVAILABLE / NOT EXPOSED`.
- The Codex runtime exposes platform tools, but the neutral benchmark instruction prohibited their use; the recovered task histories show zero model tool invocations in the 24 definitive turns.
- Frozen deterministic parsing is deliberately narrow. Prose that is not valid JSON, supported JSON-like syntax, or an unambiguous single number remains `NOT_EVALUATED`, not mathematically wrong.
- All seven semantic dimensions remain unscored pending independent review.
- Q142, Q216, Q731, and Q976 remain pending statistical adjudication; this package does not alter their frozen prose or raw responses.
- This is one model/run over 24 cases and does not establish a stable leaderboard or population-level competence.
- The Run 0 package file was unavailable for fresh rehashing; its SHA-256 appears only as explicitly labelled historical metadata.
