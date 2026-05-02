terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      Owner       = "BITS-Group23"
      Course      = "CSIZG527"
      ManagedBy   = "Terraform"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# Latest Amazon Linux 2023 AMI for x86_64
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

locals {
  azs        = slice(data.aws_availability_zones.available.names, 0, 2)
  name       = "${var.project}-${var.environment}"
  app_port   = 8000
  s3_bucket  = "${var.project}-${var.environment}-files-${random_id.suffix.hex}"
}

resource "random_id" "suffix" {
  byte_length = 3
}
