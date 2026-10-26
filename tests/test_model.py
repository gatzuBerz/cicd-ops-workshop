from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score

from ci_cd.inference import predict
from ci_cd.train import load_data, train

# Min accuracy. Test fails if test accuracy after training dips below this.
MIN_ACCURACY = 0.8
MIN_BASELINE_MARGIN = 0.05


def test_model_accuracy():
    # Train and save the model, and load it back the way deployment would.
    train()

    _, X_test, _, y_test = load_data()
    y_pred = predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    assert accuracy >= MIN_ACCURACY, (
        f"Accuracy {accuracy:.2f} is below threshold {MIN_ACCURACY:.2f}"
    )


def test_model_beats_baseline():
    train()
    X_train, X_test, y_train, y_test = load_data()
    baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    baseline_accuracy = accuracy_score(y_test, baseline.predict(X_test))
    model_accuracy = accuracy_score(y_test, predict(X_test))
    assert model_accuracy >= baseline_accuracy + MIN_BASELINE_MARGIN, (
        f"Model accuracy {model_accuracy:.2f} must beat baseline "
        f"{baseline_accuracy:.2f} by at least {MIN_BASELINE_MARGIN:.2f}"
    )
