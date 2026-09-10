# Repository Tests

Cross-cutting repository qualification lives under this directory.

`tests/repository/` validates repository contracts that are independent of CineWatch product features. Service-specific and web-specific tests are introduced with their respective implementation milestones.

`test_nexvox_engineering_corpus.py` qualifies the governed NexVox engineering-knowledge projection. It does not perform model training; it verifies corpus provenance, determinism, integrity, and training-eligibility boundaries.
