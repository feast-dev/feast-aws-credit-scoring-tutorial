from datetime import timedelta

from feast import Entity, Feature, FeatureView, FileSource, ValueType

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
