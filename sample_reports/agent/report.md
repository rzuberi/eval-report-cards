# Agent Task Evaluation Report

## Task Setup

- Project: `Toy Agent Bench`
- Task: Small coding-agent task execution
- Template: `agent`
- Dataset: Toy agent benchmark episodes
- Data split: test=6, validation=4

Evaluate a toy coding agent across bugfix, refactor, and browser-style tasks with episode-level outputs and optional action logs.

## Assumptions

- Episode confidence comes from the controller policy and is not calibrated.
- Failure mode labels are lightweight annotations rather than full root-cause analyses.

## Chosen Metrics

- Success rate is primary because the agent either completes the task or it does not.
- Reward, duration, and steps are included to show efficiency trade-offs.

## Main Results

### Overall

| episode_count | success_rate | mean_reward | mean_steps | mean_duration_seconds | mean_confidence |
| --- | --- | --- | --- | --- | --- |
| 10 | 0.5000 | 0.5620 | 9.1000 | 169.5000 | 0.7700 |

### By Split

| split | episode_count | success_rate | mean_reward | mean_steps | mean_duration_seconds | mean_confidence |
| --- | --- | --- | --- | --- | --- | --- |
| test | 6 | 0.5000 | 0.5567 | 9.3333 | 175.3333 | 0.7817 |
| validation | 4 | 0.5000 | 0.5700 | 8.7500 | 160.7500 | 0.7525 |

## Reported Metrics

| primary_metric | test_success_rate | mean_reward |
| --- | --- | --- |
| success_rate | 0.5000 | 0.5620 |

## Uncertainty / Confidence

| available | mean_confidence | note |
| --- | --- | --- |
| True | 0.7700 | Confidence reflects the agent or controller confidence column when it is available. |

## Error Slices

| column | value | count | score |
| --- | --- | --- | --- |
| environment | browser | 3 | 0.3333 |
| task_family | agent_task | 3 | 0.3333 |
| environment | config | 4 | 0.5000 |
| task_family | refactor | 4 | 0.5000 |
| environment | calculator | 3 | 0.6667 |
| task_family | bugfix | 3 | 0.6667 |

## Likely Failure Modes

- Most failed episodes cluster around dummy_secret_copy (2), test_weakened (1), unfinished_plan (1).
- Success rate drops on `environment=browser` where it falls to 0.33.
- Failed episodes often include actions such as read_secret (2), copy_to_notes (2), run_tests (1).

## Key Limitations

- No major limitations were automatically flagged.
