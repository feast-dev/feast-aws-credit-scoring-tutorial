import feast
import pandas as pd
from sklearn import svm
from joblib import dump
from sklearn.preprocessing import OrdinalEncoder

# Load loan data
loans = pd.read_parquet("data/loan_table.parquet")

# Select features from feature store to enrich loan data with
features = [
    "zipcode_features:city",
    "zipcode_features:state",
    "zipcode_features:location_type",
    "zipcode_features:tax_returns_filed",
    "zipcode_features:population",
    "zipcode_features:total_wages",
]

# Connect to your local feature store
fs = feast.FeatureStore(repo_path=".")

# Retrieve training data from BigQuery
training_df = fs.get_historical_features(entity_df=loans, features=features,).to_df()

print("Training dataset:")
print(training_df)
print()

enc = OrdinalEncoder()
categorical_features = [
    "person_home_ownership",
    "loan_intent",
    "city",
    "state",
    "location_type",
]
enc.fit(training_df[categorical_features])
training_df[categorical_features] = enc.transform(training_df[categorical_features])

# Train model
target = "loan_status"

clf = svm.SVC(gamma=0.001, C=100.0, kernel="linear")
train_X = training_df[
    training_df.columns.drop(target).drop("event_timestamp").drop("created_timestamp").drop("loan_id")
]
train_X = train_X.reindex(sorted(train_X.columns), axis=1)
train_Y = training_df.loc[:, target]
clf.fit(train_X[sorted(train_X)], train_Y)

# Save model
print("Exporting model...")
print()
dump(clf, "credit_score_model.bin")
dump(enc, "ordinal_encoder.bin")
