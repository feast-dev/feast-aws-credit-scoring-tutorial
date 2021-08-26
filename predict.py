import feast
import pandas as pd
from joblib import load


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

    def __init__(self):
        # Load model
        self.model = load("credit_score_model.bin")

        # Load ordinal encoder
        self.encoder = load("ordinal_encoder.bin")

        # Set up feature store
        self.fs = feast.FeatureStore(repo_path=".")

    def predict(self, request):
        # Get Zipcode features from Feast
        zipcode_features = self._get_zipcode_features(request)

        # Join features to request features
        features = request.copy()
        features.update(zipcode_features)
        features_df = pd.DataFrame.from_dict(features)

        # Apply ordinal encoding to categorical features
        self._apply_ordinal_encoding(features_df)

        # Sort columns
        features_df = features_df.reindex(sorted(features_df.columns), axis=1)

        # Make prediction
        features_df["prediction"] = self.model.predict(features_df)

        # return result of credit scoring
        return features_df["prediction"].iloc[0]

    def _get_zipcode_features(self, request):
        zipcode = request['zipcode'][0]

        return self.fs.get_online_features(
            entity_rows=[{"zipcode": zipcode}],
            features=self.zipcode_features,
        ).to_dict()

    def _apply_ordinal_encoding(self, request):
        request[self.categorical_features] = self.encoder.transform(request[self.categorical_features])


if __name__ == "__main__":
    loan_request = {
        "zipcode": [76104],
        "person_age": [133],
        "person_income": [59000],
        "person_home_ownership": ["RENT"],
        "person_emp_length": [123.0],
        "loan_intent": ["PERSONAL"],
        "loan_amnt": [35000],
        "loan_int_rate": [16.02],
    }

    model = CreditScoringModel()
    result = model.predict(loan_request)
    if result == 0:
        print("Loan approved")
    elif result == 1:
        print("Loan rejected")
