###############################################################################
# RDS PostgreSQL — Multi-AZ, encrypted, in private subnets.
###############################################################################

resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnets"
  subnet_ids = aws_subnet.private[*].id
  tags       = { Name = "${local.name}-db-subnets" }
}

resource "aws_db_instance" "main" {
  identifier              = "${local.name}-postgres"
  engine                  = "postgres"
  engine_version          = "15.7"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  storage_type            = "gp3"
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.data.arn

  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password

  multi_az                = true
  publicly_accessible     = false
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.db.id]

  backup_retention_period = 7
  skip_final_snapshot     = true   # academic project
  deletion_protection     = false
  apply_immediately       = true

  performance_insights_enabled = true
  performance_insights_kms_key_id = aws_kms_key.data.arn

  tags = { Name = "${local.name}-postgres" }
}
