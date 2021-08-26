# Real-time Credit Scoring with Feast on AWS

### Overview

This tutorial demonstrates the use of Feast as part of a real-time credit scoring application.
* The primary training dataset is a loan table, containing both features as well as whether an individual has defaulted on their loan
* Feast is used during training to enrich the loan table with zipcode related features from an S3 table. The S3 table is queried through Redshift.
* Feast is also used to serve the latest zipcode related features for online credit scoring using DynamoDB.
