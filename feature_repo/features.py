from datetime import timedelta

from feast import Entity, Feature, FeatureView, FileSource, ValueType

# loan = Entity(name="loan", join_key="loan_id", value_type=ValueType.INT64)

# loan_features = FeatureView(
#     name="loan_features",
#     entities=["loan", "zipcode"],
#     ttl=timedelta(days=365),
#     features=[
#         Feature(name="person_age", dtype=ValueType.INT64),
#         Feature(name="person_income", dtype=ValueType.INT64),
#         Feature(name="person_home_ownership", dtype=ValueType.STRING),
#         Feature(name="loan_intent", dtype=ValueType.STRING),
#         Feature(name="loan_amnt", dtype=ValueType.INT64),
#         Feature(name="loan_int_rate", dtype=ValueType.DOUBLE),
#         Feature(name="loan_status", dtype=ValueType.INT64),
#     ],
#     batch_source=FileSource(
#         path="data/loan_table.parquet",
#         event_timestamp_column="event_timestamp",
#         created_timestamp_column="created_timestamp",
#     ),
# )


zipcode = Entity(name="zipcode", value_type=ValueType.INT64)

zipcode_features = FeatureView(
    name="zipcode_features",
    entities=["zipcode"],
    ttl=timedelta(days=3650),
    features=[
        Feature(name="city", dtype=ValueType.STRING),
        Feature(name="state", dtype=ValueType.STRING),
        Feature(name="location_type", dtype=ValueType.STRING),
        Feature(name="tax_returns_filed", dtype=ValueType.INT64),
        Feature(name="population", dtype=ValueType.INT64),
        Feature(name="total_wages", dtype=ValueType.INT64),
    ],
    batch_source=FileSource(
        path="data/zipcode_table.parquet",
        event_timestamp_column="event_timestamp",
        created_timestamp_column="created_timestamp",
    ),
)
