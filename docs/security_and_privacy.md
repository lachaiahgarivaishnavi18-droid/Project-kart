# Security, Privacy, and Responsible Use

- No API keys, external model calls, cloud services, or network data are needed for the local application.
- `.env.example` contains configuration names only. Real secrets must remain outside source control and use a managed secret store if a future hosted service is added.
- Query input must be non-empty; numeric budget and top-K values are constrained by Streamlit controls. Catalogue columns and numeric ranges are validated on load.
- Customer preferences are passed in memory for the current recommendation and are not written to a customer database or logs.
- Explanations use product fields and ranking factors only. They explicitly label their evidence and do not infer unrepresented product claims.
- The current system has no LLM prompt surface, so prompt-injection defenses are not applicable to its execution path. If an LLM is later added, treat retrieved product text as untrusted data and separate it from instructions.
- Synthetic brands, features, prices, availability, ratings, and reviews are not real. Fairness, accessibility, coverage, and consumer impact have not been evaluated.
- No penetration test, privacy certification, threat-model review, or production security assurance is claimed.