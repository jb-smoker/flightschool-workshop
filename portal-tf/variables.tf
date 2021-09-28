#Region
variable "aws_region" {
  default = "eu-central-1"
}

variable "ssh_key" {
  description = "Public SSH key for the Linux VM"
}

variable "dns_zone" {
  description = "Route 53 DNS zone to update"
  default     = "avxlab.de"
}

#AWS Account used for S3 and DynamoDB
variable "s3_dd_aws_access_key" {
  description = "AWS Access Key for updating R53 and DynamoDB"
}
variable "s3_dd_aws_secret_key" {
  description = "AWS Secret Key for updating R53 and DynamoDB"
}
