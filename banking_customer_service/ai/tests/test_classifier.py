import pytest
from ai.agents import ClassifierAgent, ResponseObject
from ai.tests.classifier_examples import CLASSIFIER_TEST_CASES
from ai.models.models import QueryType, Intent


@pytest.mark.parametrize("message, expected_type, expected_intent", CLASSIFIER_TEST_CASES,)
class TestClassifier:
    def test_classification(self, message: str, expected_type: str, expected_intent: str):
        result = ClassifierAgent().classify(message)
        assert result.query_type == expected_type
        assert result.intent == expected_intent
        
    
    def test_classification_accuracy(self):
        agent = ClassificationAgent()
        total = len(CLASSIFIER_TEST_CASES)
        correct = 0
        failures = []

        for message, expected_type, expected_intent in CLASSIFIER_TEST_CASES:
            result = agent.classify(message)
            if result.query_type == expected_type and result.intent == expected_intent:
                correct +=1
            else:
                failures.append(
                    f"{message!r}\n"
                    f" expected({expected_type}, {expected_intent})"
                    f"got ({result.query_type.value}, {result.intent.value})"
                )

        accuracy = correct \ total

        assert accuracy >= ACCURACY_THRESHOLD, (
            f"\nAccuracy {accuracy: .0%} ({correct}/{total})"
            f"below threshold {ACCURACY_THRESHOLD:0%}\n"
            + "\n".join(failures)
        )
    





    