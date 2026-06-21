#evaluation/testcase_quality_evaluator.py
class TestcaseQualityEvaluator:

    @staticmethod
    def evaluate(testcases):

        results = {
            "total_testcases": len(testcases),
            "missing_ids": 0,
            "missing_titles": 0,
            "missing_steps": 0,
            "quality_score": 0
        }

        for tc in testcases:

            if not tc.get("id"):
                results["missing_ids"] += 1

            if not tc.get("title"):
                results["missing_titles"] += 1

            if not tc.get("steps"):
                results["missing_steps"] += 1

        penalties = (
            results["missing_ids"]
            + results["missing_titles"]
            + results["missing_steps"]
        )

        score = max(
            0,
            100 - (penalties * 5)
        )

        results["quality_score"] = score

        return results