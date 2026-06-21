#services/coverage_service.py
class CoverageService:

    @staticmethod
    def calculate(
        requirements,
        traceability_matrix
    ):

        total_requirements = len(requirements)

        covered_requirements = len(
            [
                item
                for item in traceability_matrix
                if item.testcase_ids
            ]
        )

        coverage_percentage = 0

        if total_requirements:

            coverage_percentage = round(
                (
                    covered_requirements
                    / total_requirements
                ) * 100,
                2
            )

        return {
            "total_requirements": total_requirements,
            "covered_requirements": covered_requirements,
            "coverage_percentage": coverage_percentage
        }