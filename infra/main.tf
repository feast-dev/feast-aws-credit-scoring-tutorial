resource "aws_redshift_cluster" "feast_redshift_cluster" {
  cluster_identifier = "${var.project_name}-redshift-cluster"
  iam_roles = [data.aws_iam_role.AWSServiceRoleForRedshift.arn, aws_iam_role.s3_spectrum_role.arn]
  database_name = var.database_name
  master_username = var.admin_user
  master_password = var.admin_password
  node_type = var.node_type
  cluster_type = var.cluster_type
  number_of_nodes = var.nodes

  skip_final_snapshot = true
}

resource "aws_s3_bucket" "feast_bucket" {
  bucket = "${var.project_name}-bucket"
  acl = "private"
}

data "aws_iam_role" "AWSServiceRoleForRedshift" {
  name = "AWSServiceRoleForRedshift"
}

resource "aws_iam_role" "s3_spectrum_role" {
  name = "s3_spectrum_role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "redshift.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "s3_read" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  role = aws_iam_role.s3_spectrum_role.name
}

resource "aws_iam_role_policy_attachment" "glue_full" {
  policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
  role = aws_iam_role.s3_spectrum_role.name
}

