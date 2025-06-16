I want you to help me improve the LLM as a judge (file name: kf_develop_judge.py) on all metrics: TPR, TNR, FPR, FNR.

# Current Performance

TPR (True Positive Rate/Sensitivity): 84.38%
TNR (True Negative Rate/Specificity): 72.73%
FPR (False Positive Rate): 27.27%
FNR (False Negative Rate): 15.63%

Comparison with Previous Models:
MetricModels 1 & 2Model 3ChangeTPR (Sensitivity)90.63%84.38%-6.25ppTNR (Specificity)54.55%72.73%+18.18pp ✅FPR (False Positive Rate)45.45%27.27%-18.18pp ✅FNR (False Negative Rate)9.37%15.63%+6.26pp ⚠️
Key Insights:
Major Improvements:

FPR reduced by 18.18pp: Much fewer cases where non-compliant responses are incorrectly approved
TNR improved by 18.18pp: Much better at correctly identifying non-compliant responses

Trade-offs:

FNR increased by 6.26pp: Slightly more cases where compliant responses are incorrectly rejected
TPR decreased by 6.25pp: Slightly less sensitive to truly compliant responses

Overall Assessment: The model shifted from being overly permissive to being more appropriately strict, with a much better balance between false positives and false negatives. The dramatic reduction in false positive rate (45.45% → 27.27%) is a significant improvement for dietary restriction compliance evaluation.
