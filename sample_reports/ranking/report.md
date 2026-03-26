# Retrieval Model Evaluation Report

## Task Setup

- Project: `Product Search`
- Task: Ranking candidate results
- Template: `ranking`
- Dataset: Synthetic retrieval benchmark
- Data split: test=9, validation=6

Evaluate a lightweight product retrieval model across head, tail, FAQ, and support-style queries.

## Assumptions

- Scores are comparable within a query but not across queries.
- Query groups are a useful slice for error analysis.

## Chosen Metrics

- NDCG@10 is primary because graded relevance matters.
- MRR and Hit@1 are included for first-result usefulness.

## Main Results

### Overall

| query_count | ndcg_at_3 | ndcg_at_10 | mrr | hit_at_1 | mean_top_gap |
| --- | --- | --- | --- | --- | --- |
| 5 | 0.7534 | 0.7534 | 0.6667 | 0.4000 | 0.1480 |

### By Split

| split | query_count | ndcg_at_3 | ndcg_at_10 | mrr | hit_at_1 | mean_top_gap |
| --- | --- | --- | --- | --- | --- | --- |
| test | 3 | 0.7027 | 0.7027 | 0.6111 | 0.3333 | 0.1800 |
| validation | 2 | 0.8295 | 0.8295 | 0.7500 | 0.5000 | 0.1000 |

## Reported Metrics

| primary_metric | validation_ndcg_at_10 | test_ndcg_at_10 |
| --- | --- | --- |
| ndcg_at_10 | 0.8410 | 0.7020 |

## Uncertainty / Confidence

| available | mean_top_rank_score_gap | note |
| --- | --- | --- |
| True | 0.1480 | Ranking confidence is approximated from the score gap between the top two items per query. |

## Error Slices

| column | value | count | score |
| --- | --- | --- | --- |
| query_group | support | 3 | 0.5000 |
| query_group | tail | 3 | 0.6590 |
| query_group | faq | 6 | 0.8041 |
| query_group | head | 3 | 1.0000 |

## Likely Failure Modes

- Ranking quality falls on `query_group=support` where NDCG@10 drops to 0.50.

## Key Limitations

- No major limitations were automatically flagged.
