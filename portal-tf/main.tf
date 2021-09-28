#################
## AWS  VPC
#################
resource "aws_vpc" "default" {
  cidr_block           = "10.0.0.0/24"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "avx-flightschool-vpc" }
}

resource "aws_internet_gateway" "default" {
  vpc_id = aws_vpc.default.id
  tags   = { Name = "avx-flightschool-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.default.id
  tags   = { Name = "avx-flightschool-rt" }
}

resource "aws_route" "public" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.default.id
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.default.id
  cidr_block = "10.0.0.0/26"
  tags       = { Name = "avx-flightschool-subnet" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

data "aws_route53_zone" "main" {
  name         = var.dns_zone
  private_zone = false
}

# AWS Client
data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"] # Canonical
}

data "template_file" "file" {
  template = file("${path.module}/userdata.tpl")

  vars = {
    access_key = var.s3_dd_aws_access_key
    secret_key = var.s3_dd_aws_secret_key
  }
}

resource "aws_security_group" "sg" {
  name   = "flightschool-portal-sg"
  vpc_id = aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "6"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "6"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "key" {
  key_name   = "flightschool-portal-sshkey"
  public_key = var.ssh_key
}

resource "aws_instance" "instance" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t3.small"
  key_name        = aws_key_pair.key.key_name
  subnet_id       = aws_subnet.public.id
  security_groups = [aws_security_group.sg.id]
  user_data       = data.template_file.file.rendered
  tags = {
    Name = "flightschool-portal-srv"
  }
}

resource "aws_eip" "eip" {
  vpc = true
}

resource "aws_eip_association" "eip" {
  instance_id   = aws_instance.instance.id
  allocation_id = aws_eip.eip.id
}

resource "aws_route53_record" "dns" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "flightschool.${data.aws_route53_zone.main.name}"
  type    = "A"
  ttl     = "1"
  records = [aws_eip.eip.public_ip]
}