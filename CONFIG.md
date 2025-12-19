# Miyori Configuration Guide

This document describes the various settings available in `config.json`.

## Structure Overview

The configuration is divided into functional modules:
- `speech_input`: Microphone and wake-word detection.
- `speech_output`: Text-to-speech parameters.
- `llm`: LLM backend (Gemini) settings.
- `tools`: Capability toggles and permissions.
- `memory`: Cognitive memory system settings and feature flags.

---

## [speech_input]
Controls how Miyori listens to the world.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `pause_threshold` | float | Seconds of silence after a user speaks before Miyori finishes listening. |
| `active_listen_timeout`| int | Seconds Miyori stays in "constant listening" mode before falling back to the wake word. |
| `energy_threshold` | int | Microphone sensitivity. Higher values ignore more background noise. |
| `porcupine_access_key` | string | Picovoice Access Key for wake-word detection. |
| `keyword_paths` | array | Paths to `.ppn` keyword files for Porcupine. |
| `keywords` | array | Human-readable aliases for the wake-words. |

---

## [speech_output]
Controls how Miyori speaks.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `rate` | int | The speed of speech. (Note: Specific behaviors vary by TTS engine). |

---

## [llm]
Configuration for the main "brain" (Google Gemini).

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `api_key` | string | Your Google GenAI API key. |
| `model` | string | The specific Gemini model to use for core chat (e.g., `gemini-2.5-flash-lite`). |

---

## [tools]
Enabling and restricting Miyori's capabilities.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `enabled` | boolean | Global toggle for all tools. |
| `web_search` | object | Contains `enabled` toggle for internet access. |
| `file_ops` | object | Contains `enabled` toggle and `allowed_directories` for local file access. |

---

## [memory]
The cognitive memory system configuration.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `enabled` | boolean | Global toggle for storing and retrieving memories. |
| `max_episodic_active` | int | Maximum sessions held in the "active" vector search index. |
| `max_episodic_archived`| int | Maximum count for long-term storage before oldest are pruned. |
| `token_limit` | int | Maximum tokens injected from memory into the LLM system prompt. |
| `embedding_model` | string | The model used to vectorize memories (e.g., `text-embedding-004`). |
| `verbose_logging` | boolean | If true, prints technical memory storage status to the terminal. |

### feature_flags
Toggle experimental intelligence layers.

| Flag | Default | Description |
| :--- | :--- | :--- |
| `enable_gating` | `false` | When true, Miyori uses an LLM to decide if a turn is "worth" remembering. |
| `enable_importance` | `false` | Enables calculating importance scores for better memory ranking. |
| `enable_consolidation`| `false` | Enables nightly background tasks for fact extraction and clustering. |
| `enable_contradiction_detection` | `false` | Alerts when new information conflicts with established semantic facts. |
