from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import make_scorer

from data_preprocessing import prepare_data
from modeling_evaluation import detect, show_feature_importance


# Load data
df = prepare_data()

# Features selected in the final notebook model
FEATURES = [
    "invoice_quantity",
    "avg_receving_dely",
    "Freight",
    "total_quantity",
    "total_dollar",
]

TARGET = "flagged_invoice"

X = df[FEATURES]
y = df[TARGET]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

# Scale features
scaler = StandardScaler()
x_trained = scaler.fit_transform(X_train)
x_tested = scaler.transform(X_test)


# ---------------------------------------------------------
# Compare baseline models
# ---------------------------------------------------------

model1 = LogisticRegression(random_state=42)
model1.fit(x_trained, y_train)
detect(model1, x_tested, y_test, "Logistic Regression")

model2 = DecisionTreeClassifier(random_state=42)
model2.fit(x_trained, y_train)
detect(model2, x_tested, y_test, "Decision Tree")

model3 = RandomForestClassifier(random_state=42)
model3.fit(x_trained, y_train)
detect(model3, x_tested, y_test, "Random Forest")


# ---------------------------------------------------------
# Random Forest feature importance
# ---------------------------------------------------------

feature_importance = show_feature_importance(model3, X_train.columns)
print("\nFeature Importance:")
print(feature_importance)


# ---------------------------------------------------------
# Hyperparameter tuning
# ---------------------------------------------------------

rf = RandomForestClassifier(
    random_state=42,
    n_jobs=-1,
)

param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 4, 5, 6],
    "min_samples_split": [2, 3, 5],
    "min_samples_leaf": [1, 2, 5],
    "criterion": ["gini", "entropy"],
}

scorer = make_scorer(f1_score)

grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    scoring=scorer,
    cv=5,
    verbose=2,
    n_jobs=-1,
)

grid_search.fit(x_trained, y_train)

print("\nBest Parameters:")
print(grid_search.best_params_)

print("\nBest F1 Score:")
print(grid_search.best_score_)

best_model = grid_search.best_estimator_

y_pred = best_model.predict(x_tested)
test_f1 = f1_score(y_test, y_pred)

print("\nTest F1 Score:")
print(test_f1)
