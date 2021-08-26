resource "aws_redshift_cluster" "feast_redshift_cluster" {
  cluster_identifier = "${var.project_name}-redshift-cluster"
  iam_roles = ["AWSServiceRoleForRedshift", aws_iam_role.s3_spectrum_role.name]
  database_name = var.database_name
  master_username = var.admin_user
  master_password = var.admin_password
  node_type = var.node_type
  cluster_type = var.cluster_type
  number_of_nodes = var.nodes
}

resource "aws_s3_bucket" "feast_bucket" {
  bucket = "${var.project_name}-bucket"
  acl = "private"
}

resource "aws_iam_role" "s3_spectrum_role" {
  name = "s3_spectrum_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
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

