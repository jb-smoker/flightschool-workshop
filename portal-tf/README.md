# portal-tf

### Description

This will launch the Pod Registration portal for Aviatrix FlightSchool.  The following will be created:

* VPC, Subnet, IGW
* Ubuntu EC2 Instance
* Route53 host records

### Usage

Create a new FlightSchool session and access code:

* Go to:  https://flightschool.avxlab.de/new
* Enter in the max number of pods, and starting pods (ie. max pods = 45, starting pod = 1)
* Click New and note the Access Code

View current registrations:

* Go to:  https://flightschool.avxlab.de/list

View attendee progress:

* Go to:  https://flightschool.avxlab.de/status

### Variables
The following variables are required:

key | value
--- | ---
s3_dd_aws_access_key | AWS Access Key for Route53 and S3
s3_dd_aws_secret_key | AWS Secret Key for Route53 and S3
ssh_key | Client SSH key
