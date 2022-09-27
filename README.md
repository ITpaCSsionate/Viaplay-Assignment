** THE APP HAS BEEN SHUT DOWN FOR COSTS AFTER THE INTERVIEW **
# Where can I access the app?
**"Dynamic" setup -> [HERE](http://viaplayassignment-1452398108.eu-west-1.elb.amazonaws.com/hello)**

**Static setup -> [HERE](http://ViaPlayAssignmentstatic-134299611.eu-west-1.elb.amazonaws.com/hello)**


# App
Just a simple Flask API exposing /healthz and /hello endpoints. The root (/) redirects to /hello.


# IaC and IaC_Static
Folders containing two possible solutions for the assignment.
The folders have a Configuration and a Src subfolders. The Configuration folder has a .json with some parameters (more could be added). The Src folders have the python script for creating the CloudFormation Stack, a bash script for creating certificates (for configuring ssh access to the VMs), and an ECR script for creating a CloudFormation stack that creates an ECR repository. 


## Considerations -- common
There are common needed resources for both setups: the vpc, the security groups, the route tables IAM policies so that ECS can work properly and pull ECR images, endpoints (the subnets where the ec2 vms are private), etc. 

The security groups between the VMs are quite permissive -they allow all the traffic coming from inside the VPC. The only one "restrictive" is the one applied to the LB. There is also a SG for the Bastion instance that allows SSH from all internet and TCP/UDP from within the VPC (one of the first approaches followed was to setup a NAT instance and a Bastion in the same host for expense reduction for connecting to docker registry, but was discarded in favour of ECR). 

Fargate was discarded as it is more expensive than EC2 and not included in the Free Tier. As a result, awsvpc networking mode was not available for ECS. ACLs have not been created as there is no external connectivity and the traffic is only http. If the application had to connect to an external IP (for example), or segregated workloads were deployed in the subnets, an ACL would make more sense. 

## Considerations -- IaC
The setup achieved with this can scale horizontally. EC2 vms are created in an AutoScaling Group and scale based on cpu usage. ECS tasks are also configured so that they can scale horizontally based on cpu usage also. 


## Considerations -- IaC_Static
The setup achieved with this script is a static one, i.e, EC2 VMs are added to the ALB and there is only 1 ECS task running for each VM (as the task runs using the host networking mode). For this reason, the scalability of this setup is somewhat limited and would require further human interaction. 

# How to reproduce
> This explains how to reproduce the Dynamic version. The Static one can be reproduced similarly by doing the mentioned steps in the IaC_Static folder
1- Clone the repo 

2- Execute [this](./IaC/Src/createECR.py) script. It will create a CloudFormation template that can be used to create a repository to push the image.

3- Build the container image. There is a very simple [script](./App/Src/build.sh) that does so for you (however you need to modify the repository). Specify your ECR repository. You should have loged in to the repository previously.

4- Modify the parameters in [this configuration file](./IaC/Configuration/Configuration.json). At least you need to modify: 
    - the dockerImage (it needs to point to your generated image)

5- Execute [this bash script](./IaC/Src/generateNodeKeys.sh). It will generate 4 files containing public/private keys.

6- Execute [this script](./IaC/Src/createInfra.py). It will print a YAML with the CloudFormation template you should execute later on for creating everything.

7- Execute the previously obtained CloudFormation template. You will be able to access the application by using the URL of the LB created (it is internet-facing). Take into account:
    - No HTTPs has been configured. Port 80 is the port the LB listens at
    - There are two endpoints of the application: /healthz and /hello. Hello is the requested one in the assignment


# Improvements
0. Document code

1. SSL/TLS

2. ACLs

3. More restrictive SG's

4. More customisations



# References used
- Official AWS CloudFormation User Guide (for knowing the parameters)
- Troposphere documentation and examples
- StackOverflow (debugging, errors...)

