# KV Cache

**Question:** How does KV cache shape long-context inference and memory use?

This directory contains daily research-map notes for this topic.

## Reading List

| Date | Paper | Summary |
|------|-------|---------|
| 2026-07-15 | [KIVI: 2-bit Asymmetric KV Cache Quantization](2026-07-15-kv-cache.md) | Tuning-free asymmetric KV cache quantization; per-channel keys, per-token values |
| 2026-07-22 | [Make Each Token Count (Eviction)](2026-07-22-kv-cache.md) | Learned importance-aware eviction with eviction-aware training; StreamingLLM comparison |
| 2026-07-29 | [ShadowKV: Offloading via Low-Rank Key Cache](2026-07-29-kv-cache.md) | Low-rank key compression + value cache offloading; on-the-fly sparse KV reconstruction |
