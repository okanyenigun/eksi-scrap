# 0.0.3 - 2026-01-08

### Changed

- Made the `langchain` import in `eksiminer/extensions/langchain/tools.py` optional and lazy-loaded. Now, `langchain` is only imported when a tool function is called, improving compatibility for users who do not require these features.

### Added

- Added `channel` argument to `get_gundem` for filtering popular topics by channel.
- Added `extensions` module, including tools for LangChain integration under `eksiminer/extensions/langchain/tools.py`.
