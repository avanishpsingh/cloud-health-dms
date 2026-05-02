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
  engine_version          = "15.10"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  storage_type            = "gp3"
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.data.arn

  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password

  multi_az                = false   # free-tier: Multi-AZ not supported
  publicly_accessible     = true    # temp: for seeding from laptop, revert after
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.db.id, aws_security_group.db_seed.id]

  backup_retention_period = 0       # free-tier: backup retention must be 0
  skip_final_snapshot     = true    # academic project
  deletion_protection     = false
  apply_immediately       = true

  performance_insights_enabled = false  # free-tier: Performance Insights not supported

  tags = { Name = "${local.name}-postgres" }
}

# Temp SG: allow laptop IP to connect on 5432 for seeding. Remove after seed.
resource "aws_security_group" "db_seed" {
  name        = "${local.name}-db-seed-sg"
  description = "Temp seed access from dev laptop"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["152.58.130.186/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
