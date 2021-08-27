import boto3
import pandas as pd

from credit_model import CreditScoringModel

# Get historic loan data from S3
s3 = boto3.client("s3").download_file(
    "my-feast-project-bucket", "loan_features/table.parquet", "loan_table.parquet"
)
loans = pd.read_parquet("loan_table.parquet")

# Create model
model = CreditScoringModel()

# Train model (using Redshift for zipcode features)
model.train(loans)

# Make online prediction (using DynamoDB for zipcode features)
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

result = model.predict(loan_request)

if result == 0:
    print("Loan approved!")
elif result == 1:
    print("Loan rejected!")
