variable "project" {
  description = "Project short name; used as a prefix for all resources."
  type        = string
  default     = "healthdms"
}

variable "environment" {
  description = "Deployment environment (dev / staging / prod)."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "ap-south-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "instance_type" {
  description = "EC2 instance type for the FastAPI app."
  type        = string
  default     = "t3.micro"
}

variable "asg_min" {
  type    = number
  default = 1
}

variable "asg_max" {
  type    = number
  default = 3
}

variable "asg_desired" {
  type    = number
  default = 2
}

variable "key_pair_name" {
  description = "Existing EC2 key pair name for SSH access (optional)."
  type        = string
  default     = ""
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_name" {
  type    = string
  default = "healthdms"
}

variable "db_username" {
  type    = string
  default = "healthadmin"
}

variable "db_password" {
  description = "Master password for RDS. Pass via -var or TF_VAR_db_password — never commit."
  type        = string
  sensitive   = true
}

variable "app_repo_url" {
  description = "Public git URL the EC2 user-data script clones at boot."
  type        = string
  default     = "https://github.com/avanishpsingh/cloud-health-dms.git"
}

variable "app_repo_ref" {
  type    = string
  default = "main"
}

variable "alarm_email" {
  description = "Email to subscribe to alarm/reminder SNS topic. Leave empty to skip."
  type        = string
  default     = ""
}
