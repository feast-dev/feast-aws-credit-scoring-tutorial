import feast
import pandas as pd
from sklearn import tree
from sklearn.preprocessing import OrdinalEncoder


class CreditScoringModel:
    categorical_features = [
        "person_home_ownership",
        "loan_intent",
        "city",
        "state",
        "location_type",
    ]

    zipcode_features = [
        "zipcode_features:city",
        "zipcode_features:state",
        "zipcode_features:location_type",
        "zipcode_features:tax_returns_filed",
        "zipcode_features:population",
        "zipcode_features:total_wages",
    ]

    target = "loan_status"

    def __init__(self):
        # Load model
        self.classifier = tree.DecisionTreeClassifier()

        # Load ordinal encoder
        self.encoder = OrdinalEncoder()

        # Set up feature store
        self.fs = feast.FeatureStore(repo_path="feature_repo")

    def train(self, loans):
        training_df = self._get_historical_zipcode_features(loans)

        self._fit_ordinal_encoder(training_df)
        self._apply_ordinal_encoding(training_df)

        train_X = training_df[
            training_df.columns.drop(self.target)
            .drop("event_timestamp")
            .drop("created_timestamp")
            .drop("loan_id")
        ]
        train_X = train_X.reindex(sorted(train_X.columns), axis=1)
        train_Y = training_df.loc[:, self.target]
        self.classifier.fit(train_X[sorted(train_X)], train_Y)

    def _get_historical_zipcode_features(self, loans):
        return self.fs.get_historical_features(
            entity_df=loans, features=self.zipcode_features
        ).to_df()

    def _fit_ordinal_encoder(self, requests):
        self.encoder.fit(requests[self.categorical_features])

    def _apply_ordinal_encoding(self, requests):
        requests[self.categorical_features] = self.encoder.transform(
            requests[self.categorical_features]
        )

    def predict(self, request):
        # Get Zipcode features from Feast
        zipcode_features = self._get_online_zipcode_features(request)

        # Join features to request features
        features = request.copy()
        features.update(zipcode_features)
        features_df = pd.DataFrame.from_dict(features)

        # Apply ordinal encoding to categorical features
        self._apply_ordinal_encoding(features_df)

        # Sort columns
        features_df = features_df.reindex(sorted(features_df.columns), axis=1)

        # Make prediction
        features_df["prediction"] = self.classifier.predict(features_df)

        # return result of credit scoring
        return features_df["prediction"].iloc[0]

    def _get_online_zipcode_features(self, request):
        zipcode = request["zipcode"][0]

        return self.fs.get_online_features(
            entity_rows=[{"zipcode": zipcode}], features=self.zipcode_features,
        ).to_dict()
