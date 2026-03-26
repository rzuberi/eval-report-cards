# Support Ticket Classifier Evaluation Report

## Task Setup

- Project: `Support Ticket Triage`
- Task: Urgency classification
- Template: `classification`
- Dataset: Internal synthetic support-ticket benchmark v1
- Data split: test=8, train=6, validation=4

Evaluate a three-class urgency classifier for incoming support tickets across web, email, and API sources.

## Assumptions

- The supplied confidence is the model confidence for the predicted class.
- Email traffic is expected to be noisier than API or web traffic.

## Chosen Metrics

- Macro F1 is primary because class balance matters.
- Accuracy is included for quick operational interpretation.

## Main Results

### Overall

| count | accuracy | macro_precision | macro_recall | macro_f1 | per_label | confusion |
| --- | --- | --- | --- | --- | --- | --- |
| 18 | 0.7778 | 0.7937 | 0.7937 | 0.7778 | label=high, support=7, precision=1.0000, recall=0.7143, f1=0.8333, label=low, support=5, precision=0.7143, recall=1.0000, f1=0.8333, label=medium, support=6, precision=0.6667, recall=0.6667, f1=0.6667 | high=high=5, low=0, medium=2, low=high=0, low=5, medium=0, medium=high=0, low=2, medium=4 |

### By Split

| split | count | accuracy | macro_precision | macro_recall | macro_f1 | per_label | confusion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| test | 8 | 0.7500 | 0.7778 | 0.7778 | 0.7556 | label=high, support=3, precision=1.0000, recall=0.6667, f1=0.8000, label=low, support=2, precision=0.6667, recall=1.0000, f1=0.8000, label=medium, support=3, precision=0.6667, recall=0.6667, f1=0.6667 | high=high=2, low=0, medium=1, low=high=0, low=2, medium=0, medium=high=0, low=1, medium=2 |
| train | 6 | 0.8333 | 0.8889 | 0.8333 | 0.8222 | label=high, support=2, precision=1.0000, recall=1.0000, f1=1.0000, label=low, support=2, precision=0.6667, recall=1.0000, f1=0.8000, label=medium, support=2, precision=1.0000, recall=0.5000, f1=0.6667 | high=high=2, low=0, medium=0, low=high=0, low=2, medium=0, medium=high=0, low=1, medium=1 |
| validation | 4 | 0.7500 | 0.8333 | 0.8333 | 0.7778 | label=high, support=2, precision=1.0000, recall=0.5000, f1=0.6667, label=low, support=1, precision=1.0000, recall=1.0000, f1=1.0000, label=medium, support=1, precision=0.5000, recall=1.0000, f1=0.6667 | high=high=1, low=0, medium=1, low=high=0, low=1, medium=0, medium=high=0, low=0, medium=1 |

## Reported Metrics

| primary_metric | overall_accuracy | overall_macro_f1 |
| --- | --- | --- |
| macro_f1 | 0.7778 | 0.7685 |

## Uncertainty / Confidence

| available | mean_correct_confidence | mean_error_confidence | high_confidence_error_rate | bootstrap_ci_95 |
| --- | --- | --- | --- | --- |
| True | 0.7921 | 0.7250 | 0.0000 | 0.6400, 0.8700 |

## Error Slices

| column | value | count | score |
| --- | --- | --- | --- |
| source | email | 4 | 0.0000 |
| region | south | 9 | 0.5556 |
| region | north | 9 | 1.0000 |
| source | web | 8 | 1.0000 |
| source | api | 6 | 1.0000 |

## Likely Failure Modes

- Performance drops on `source=email` where accuracy falls to 0.00.
- Wrong predictions are often still made with fairly high confidence.

## Key Limitations

- No major limitations were automatically flagged.
