# HuggingFace Loading Reference

> Load when: working with HuggingFace datasets for the first time, encountering auth errors, or choosing between repos and buckets.

## HF URI Patterns

| Pattern | Type | Example |
|---------|------|---------|
| `hf://datasets/org/name` | Dataset repo | `hf://datasets/stanfordnlp/imdb` |
| `hf://datasets/org/name@revision` | Specific version | `hf://datasets/org/name@v1.0` |
| `org/name` | Short form (dataset assumed) | `stanfordnlp/imdb` |
| `hf://buckets/org/bucket` | Storage bucket | `hf://buckets/org/my-checkpoint-bucket` |

## Token Resolution Chain

```
1. --token-env flag value (explicit env var name)
2. HF_TOKEN env var
3. HUGGING_FACE_HUB_TOKEN env var (legacy)
4. Cached CLI login (~/.cache/huggingface/token)
5. None (public access only)
```

Token cleaning: always strip `\r`, `\n`, and leading/trailing whitespace before use.

## Datasets Server API Reference

Base URL: `https://datasets-server.huggingface.co`

| Endpoint | Purpose | Key params |
|----------|---------|------------|
| `/splits?dataset=org/name` | List configs and splits | `dataset` |
| `/info?dataset=org/name&config=default` | Schema, row counts | `dataset`, `config` |
| `/first-rows?dataset=org/name&config=default&split=train` | Sample rows | `dataset`, `config`, `split` |
| `/parquet?dataset=org/name` | List parquet files with sizes | `dataset` |
| `/is-valid?dataset=org/name` | Check if dataset is valid | `dataset` |

Auth: `Authorization: Bearer {token}` header for private/gated datasets.

## Repos vs Buckets

| Need | Use | Why |
|------|-----|-----|
| Publish a cleaned dataset | Dataset Repo | Versioning, dataset card, community access |
| Store training checkpoints | Bucket | Mutable, no versioning overhead |
| Share with team (versioned) | Dataset Repo (private) | PR workflow, discussions |
| Archive large raw data | Bucket | rsync-like sync, dedup |
| Deliver to HF for fine-tuning | Dataset Repo | Reproducible with revision pins |

## Visibility Matrix

| Mode | API param | Who can read | Dataset card needed |
|------|-----------|-------------|-------------------|
| Public | `private=False` | Anyone | Recommended |
| Private | `private=True` | Owner + collaborators | No |
| Gated (auto) | `gated="auto"` | After agreeing to terms | Yes |
| Gated (manual) | `gated="manual"` | After owner approval | Yes |
| Organization | `repo_id="org/name"` | Org members | No |

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| GatedRepoError | Dataset requires access approval | Guide user to `https://huggingface.co/datasets/{repo}` |
| RepositoryNotFoundError | Wrong name or no access | Check repo name and token |
| 401 Unauthorized | Token invalid or expired | Re-run `huggingface-cli login` |
| 429 Too Many Requests | Rate limited | Automatic retry with backoff |

## Enterprise / Private Hub

Set `HF_ENDPOINT` env var to redirect all API calls to a self-hosted Hub instance:

```bash
export HF_ENDPOINT="https://hub.your-company.com"
```

All `huggingface_hub` API calls respect this variable. Tokens are issued by the enterprise instance, not huggingface.co.
