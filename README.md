# Real-time Credit Scoring with Feast on AWS

## Overview

This tutorial demonstrates the use of Feast as part of a real-time credit scoring application.
* The primary training dataset is a loan table, containing both features as well as whether an individual has defaulted on their loan
* Feast is used during training to enrich the loan table with zipcode related features from an S3 table. The S3 table is queried through Redshift.
* Feast is also used to serve the latest zipcode related features for online credit scoring using DynamoDB.

## Requirements

* Terraform (v1.0 or later)
* AWS CLI (v2.2 or later)

## Setup

### Setting up Redshift and S3

First we will set up your data infrastructure to simulate a production environment. We will deploy Redshift, an S3 
bucket containing our zipcode feature parquet file, IAM roles and policies for Redshift to access S3, and create a 
Redshift table that can query the parquet file. 

Initialize Terraform
```
cd infra
terraform init
```

Make sure the Terraform plan looks good
```
terraform plan -var="admin_password=thisISyourPassword1"
```

Deploy your infrastructure
```
terraform apply -var="admin_password=thisISyourPassword1"
```

Once your infrastructure is deployed, you should see the following outputs from Terraform
```
redshift_cluster_identifier = "my-feast-project-redshift-cluster"
redshift_spectrum_arn = "arn:aws:iam::<Account>:role/s3_spectrum_role"
redshift_table = "zipcode_features"
```

Next we create a mapping from the Redshift cluster to the external catalog
```
aws redshift-data execute-statement \
    --region us-west-2 \
    --cluster-identifier [SET YOUR redshift_cluster_identifier HERE] \
    --db-user admin \
    --database dev --sql "create external schema spectrum from data catalog database 'dev' iam_role \
    '[SET YOUR redshift_spectrum_arn here]' create external database if not exists;"
```

To see whether the command was successful, please run the following command (substitute your statement id)
```
aws redshift-data describe-statement --id [SET YOUR STATEMENT ID HERE]
``` 

You should now be able to query actual zipcode features by executing the following statement
```
aws redshift-data execute-statement \
    --region us-west-2 \
    --cluster-identifier [SET YOUR redshift_cluster_identifier HERE] \
    --db-user admin \
    --database dev --sql "SELECT * from spectrum.zipcode_features LIMIT 1;"
```
which should print out results by running
```
aws redshift-data get-statement-result --id [SET YOUR STATEMENT ID HERE]
```

Return to the root of the credit scoring repo
```
cd ..
```

### Setting up Feast

Install Feast using pip

```
pip install feast
```

We have already set up a feature repository in [feature_repo/](feature_repo/). It isn't necessary to create a new
feature repository, but it can be done using the following command
```
feast init -t aws feature_repo # Command only shown for reference.
```

Since we don't need to `init` a new repository, all we have to do is configure the 
[feature_store.yaml/](feature_repo/feature_store.yaml) in the feature repository. Please set the fields under
`offline_store` to the configuration you have received when deploying your Redshift cluster and S3 bucket.

Deploy the feature store by running `apply` from within the `feature_repo/` folder
```
feast apply
```
```
Registered entity zipcode
Registered feature view zipcode_features
Deploying infrastructure for zipcode_features
```

Next we load features into the online store using the `materialize-incremental` command. This command will load the
latest feature values from a data source into the online store.

```
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")
feast materialize-incremental $CURRENT_TIME
```

## Train and test the model

Finally, we train the model using a combination of loan data from S3 and zipcode features from Redshift
(which in turn queries S3), and then we test online inference by reading zipcode features from DynamoDB 

```
python run.py
```
The script should then output the result of a single loan application
```
loan rejected!
```

