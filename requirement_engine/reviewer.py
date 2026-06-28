#requirement__engine/reviewer.py
class RequirementReviewer:
    """
    Reviews requirements from a QA perspective.

    This component identifies ambiguity,
    missing business information,
    assumptions,
    and clarification questions.

    It prepares the requirement
    for AI Test Design.
    """

    @staticmethod
    def review(requirements):

        reviewed = []

        for req in requirements:

            questions = []

            text = req["text"].lower()

            if "login" in text:
                questions.extend([
                    "What authentication mechanism is used?",
                    "Are failed login attempts limited?",
                    "Is MFA required?"
                ])

            if "create" in text:
                questions.append(
                    "What mandatory fields are required?"
                )

            if "delete" in text:
                questions.append(
                    "Is delete soft-delete or permanent?"
                )

            if "email" in text:
                questions.append(
                    "Should email uniqueness be validated?"
                )

            if "shall" not in text:
                questions.append(
                    "Requirement wording may be ambiguous."
                )

            req["review"] = {
                "clarification_questions": questions,
                "needs_sme": len(questions) > 0
            }

            reviewed.append(req)

        return reviewed