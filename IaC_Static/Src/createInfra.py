from troposphere import Ref, Template, Base64, Join, GetAtt, Tags
import troposphere.ec2 as ec2 
import troposphere.ecs as ecs
import troposphere.elasticloadbalancingv2 as elb
from troposphere.iam import InstanceProfile, PolicyType, Role

import json

configuration = json.load(open("../Configuration/Configuration.json", 'r'))
tagsC = configuration["tags"]
tags = Tags(tagsC)
region = configuration["region"]
ecsClusterName = configuration["ecsClusterName"]
testImage = configuration["dockerImage"]
keyNames = configuration["keyNames"]

t = Template()



vpc = t.add_resource(
    ec2.VPC(
        "ViaPlayTeststatic", 
        CidrBlock="10.0.0.0/16", 
        EnableDnsHostnames=True, 
        EnableDnsSupport=True, 
        Tags=tags
    )
)

subnet1a = t.add_resource(
    ec2.Subnet(
        "PrivateSubnet1astatic", 
        CidrBlock="10.0.0.0/18", 
        AvailabilityZone="eu-west-1a", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

subnet1b = t.add_resource(
    ec2.Subnet(
        "PrivateSubnet1bstatic", 
        CidrBlock="10.0.64.0/18", 
        AvailabilityZone="eu-west-1b", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

subnet1c = t.add_resource(
    ec2.Subnet(
        "PrivateSubnet1cstatic", 
        CidrBlock="10.0.128.0/18", 
        AvailabilityZone="eu-west-1c", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

subnetAdministration1a = t.add_resource(
    ec2.Subnet(
        "Administration1astatic", 
        CidrBlock="10.0.192.0/19", 
        AvailabilityZone="eu-west-1a", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)
subnetAdministration1b = t.add_resource(
    ec2.Subnet(
        "Administration1bstatic", 
        CidrBlock="10.0.224.0/19", 
        AvailabilityZone="eu-west-1b", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

vpcIngressTCP = ec2.SecurityGroupRule("ingressTCPstatic", IpProtocol="tcp", FromPort="0", ToPort="65535", CidrIp="10.0.0.0/16")
vpcIngressUDP = ec2.SecurityGroupRule("ingressUDPstatic", IpProtocol="udp", FromPort="0", ToPort="65535", CidrIp="10.0.0.0/16")

vpcEgressTCP = ec2.SecurityGroupRule("egressTCPstatic", IpProtocol="tcp", FromPort="0", ToPort="65535", CidrIp="0.0.0.0/0")
vpcEgressUDP = ec2.SecurityGroupRule("egressUDPstatic", IpProtocol="udp", FromPort="0", ToPort="65535", CidrIp="0.0.0.0/0")

HTTPIngress = ec2.SecurityGroupRule("ingressTCPstatic", IpProtocol="tcp", FromPort="80", ToPort="80", CidrIp="0.0.0.0/0")

allowAllIntheSubnetSG = t.add_resource(
    ec2.SecurityGroup(
        "generalSGstatic", 
        GroupDescription="allows everything in the private subnet", 
        SecurityGroupIngress=[vpcIngressTCP, vpcIngressUDP], 
        VpcId=Ref(vpc), 
        SecurityGroupEgress=[vpcEgressTCP, vpcEgressUDP], 
        Tags=tags
    )
)


ecsAgentEndpoint = t.add_resource(
    ec2.VPCEndpoint(
        "ecsAgentstatic", 
        VpcEndpointType="Interface", 
        PrivateDnsEnabled=True, 
        ServiceName="com.amazonaws.eu-west-1.ecs-agent", 
        VpcId=Ref(vpc), 
        SubnetIds=[Ref(subnet1a), Ref(subnet1b), Ref(subnet1c)], 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")]
    )
)

ecsTelemetryEndpoint = t.add_resource(
    ec2.VPCEndpoint(
        "ecsTelemetrystatic", 
        VpcEndpointType="Interface", 
        PrivateDnsEnabled=True, 
        ServiceName="com.amazonaws.eu-west-1.ecs-telemetry", 
        VpcId=Ref(vpc), SubnetIds=[Ref(subnet1a), Ref(subnet1b), Ref(subnet1c)], 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")]
    )
)

ecsEndpoint = t.add_resource(
    ec2.VPCEndpoint(
        "ecsstatic", 
        VpcEndpointType="Interface", 
        PrivateDnsEnabled=True, 
        ServiceName="com.amazonaws.eu-west-1.ecs", 
        VpcId=Ref(vpc), 
        SubnetIds=[Ref(subnet1a), Ref(subnet1b), Ref(subnet1c)], 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")]
    )
)

ecrApiEndpoint = t.add_resource(
    ec2.VPCEndpoint(
        "ecrApistatic", 
        VpcEndpointType="Interface", 
        PrivateDnsEnabled=True, 
        ServiceName="com.amazonaws.eu-west-1.ecr.api", 
        VpcId=Ref(vpc), 
        SubnetIds=[Ref(subnet1a), Ref(subnet1b), Ref(subnet1c)], 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")]
    )
)

ecrDkrEndpoint = t.add_resource(
    ec2.VPCEndpoint(
        "ecrDkrstatic", 
        VpcEndpointType="Interface", 
        PrivateDnsEnabled=True, 
        ServiceName="com.amazonaws.eu-west-1.ecr.dkr", 
        VpcId=Ref(vpc), 
        SubnetIds=[Ref(subnet1a), Ref(subnet1b), Ref(subnet1c)], 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")]
    )
)




internetGateway = t.add_resource(
    ec2.InternetGateway(
        "IGWstatic", 
        Tags=tags
    )
)

internetGatewayAttachment = t.add_resource(
    ec2.VPCGatewayAttachment(
        "igwAstatic", 
        InternetGatewayId=Ref(internetGateway), 
        VpcId=Ref(vpc)
    )
)

routeTableAdministration = t.add_resource(
    ec2.RouteTable(
        "RTadministrationstatic", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)


routeAdminstration = t.add_resource(
    ec2.Route(
        "routeAdministrationstatic", 
        DestinationCidrBlock="0.0.0.0/0", 
        GatewayId=Ref(internetGateway), 
        RouteTableId=Ref(routeTableAdministration)
    )
)

## Reference: https://aws.amazon.com/premiumsupport/knowledge-center/public-load-balancer-private-ec2/
routeTableAdministrationAssociation1a = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "adminrtassoc1astatic", 
        RouteTableId=Ref(routeTableAdministration), 
        SubnetId=Ref(subnetAdministration1a)
    )
)

routeTableAdministrationAssociation1b = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "adminrtassoc1bstatic", 
        RouteTableId=Ref(routeTableAdministration), 
        SubnetId=Ref(subnetAdministration1b)
    )
)

t.add_resource(
    ec2.KeyPair(
        keyNames[0],
        KeyName=keyNames[0],
        KeyType="rsa",
        PublicKeyMaterial=open(keyNames[0]+".pub",'r').read(), 
        Tags=tags
    )
)

t.add_resource(
    ec2.KeyPair(
        keyNames[1],
        KeyName=keyNames[1],
        KeyType="rsa",
        PublicKeyMaterial=open(keyNames[1]+".pub",'r').read(), 
        Tags=tags
    )
)

sshIngress =  ec2.SecurityGroupRule(
    "sshIngressstatic", 
    IpProtocol="tcp", 
    FromPort="22", 
    ToPort="22", 
    CidrIp="0.0.0.0/0"
)

bastionInstanceSG = t.add_resource(
    ec2.SecurityGroup(
        "bastionInstanceSGstatic", 
        GroupDescription="sg for nat gw instance", 
        SecurityGroupIngress=[vpcIngressTCP, vpcIngressUDP, sshIngress], 
        VpcId=Ref(vpc), 
        SecurityGroupEgress=[vpcEgressTCP, vpcEgressUDP], 
        Tags=tags
    )
)


bastionInstance = t.add_resource(
    ec2.Instance(
        "bastionInstancestatic", 
        ImageId="ami-096800910c1b781ba", 
        InstanceType="t2.micro", 
        SubnetId=Ref(subnetAdministration1a), 
        SecurityGroupIds=[GetAtt(bastionInstanceSG, "GroupId")],
        KeyName=keyNames[1], 
        Tags=tags
    )
)

elasticIp = t.add_resource(
    ec2.EIP(
        "bastionInstanceEIPstatic", 
        InstanceId=Ref(bastionInstance), 
        Tags=tags
    )
)

elasticIpAssociation = t.add_resource(
    ec2.EIPAssociation(
        "bastionInstanceEIPAssociationstatic", 
        EIP=Ref(elasticIp), 
        InstanceId=Ref(bastionInstance)
    )
)

routeTable = t.add_resource(
    ec2.RouteTable(
        "routeTablestatic", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

s3Endpoint = t.add_resource(
    ec2.VPCEndpoint(
        "S3static", 
        VpcEndpointType="Gateway", 
        ServiceName="com.amazonaws.eu-west-1.s3", 
        VpcId=Ref(vpc), 
        RouteTableIds=[Ref(routeTableAdministration), Ref(routeTable)]
    )
)

routeTable1aAssociation = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "1artassocstatic", 
        RouteTableId=Ref(routeTable), 
        SubnetId=Ref(subnet1a)
    )
)

routeTable1bAssociation = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "1brtassocstatic", 
        RouteTableId=Ref(routeTable), 
        SubnetId=Ref(subnet1b)
    )
)

routeTable1cAssociation = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "1crtassocstatic", 
        RouteTableId=Ref(routeTable), 
        SubnetId=Ref(subnet1c)
    )
)




EcsClusterRole = t.add_resource(
    Role(
        "EcsClusterRolestatic",
        Path="/",
        ManagedPolicyArns=["arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"],
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        }, 
        Tags=tags
    )
)

PolicyEcs = t.add_resource(
    PolicyType(
        "PolicyEcsstatic",
        PolicyName="EcsPolicy",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "ecs:CreateCluster",
                        "ecs:RegisterContainerInstance",
                        "ecs:DeregisterContainerInstance",
                        "ecs:DiscoverPollEndpoint",
                        "ecs:Submit*",
                        "ecs:Poll",
                        "ecs:StartTelemetrySession",
                    ],
                    "Resource": "*",
                    "Effect": "Allow",
                }
            ],
        },
        Roles=[Ref(EcsClusterRole)]
    )
)

PolicyEcr = t.add_resource(
    PolicyType(
        "PolicyEcrstatic",
        PolicyName="EcrPolicy",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:BatchGetImage",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:GetAuthorizationToken"
                    ],
                    "Resource": "*"
                }
            ],
        },
        Roles=[Ref(EcsClusterRole)]
    )
)

EC2InstanceProfile = t.add_resource(
    InstanceProfile(
        "EC2InstanceProfilestatic",
        Path="/",
        Roles=[Ref(EcsClusterRole)]
    )
)

ecsCluster = t.add_resource(
    ecs.Cluster(ecsClusterName, Tags=tags)
)

userData = Base64(Join("", ["#!/bin/bash\necho ECS_CLUSTER=", Ref(ecsCluster), " >> /etc/ecs/ecs.config"]))
instance1a = t.add_resource(
    ec2.Instance(
        "1aInstancestatic", 
        ImageId="ami-0e592a261c043bc6a", 
        InstanceType="t2.micro", 
        SubnetId=Ref(subnet1a), 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")], 
        KeyName=keyNames[0], 
        UserData=userData,
        IamInstanceProfile=Ref(EC2InstanceProfile), 
        Tags=tags
    )
)

instance1b = t.add_resource(
    ec2.Instance(
        "1bInstancestatic", 
        ImageId="ami-0e592a261c043bc6a", 
        InstanceType="t2.micro", 
        SubnetId=Ref(subnet1b), 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")], 
        KeyName=keyNames[0], 
        UserData=userData,
        IamInstanceProfile=Ref(EC2InstanceProfile), 
        Tags=tags
    )
)





allowHTTPSG = t.add_resource(
    ec2.SecurityGroup(
        "AllowHTTPstatic", 
        GroupDescription="AllowHTTP", 
        SecurityGroupIngress=[HTTPIngress], 
        VpcId=Ref(vpc), 
        SecurityGroupEgress=[vpcEgressTCP, vpcEgressUDP], 
        Tags=tags
    )
)


alb = t.add_resource(
    elb.LoadBalancer(
        "ViaPlayAssignmentLBstatic", 
        Name="ViaPlayAssignmentstatic", 
        Scheme="internet-facing", 
        Subnets=[
            Ref(subnetAdministration1a), Ref(subnetAdministration1b)
        ], 
        SecurityGroups=[
            Ref(allowHTTPSG)
        ], 
        Tags=tags
    )
)

targetGroup = t.add_resource(
    elb.TargetGroup(
        "APPtgstatic", 
        HealthCheckIntervalSeconds="30", 
        HealthCheckPath="/healthz", 
        HealthCheckProtocol="HTTP", 
        HealthCheckTimeoutSeconds="10", 
        HealthyThresholdCount="4", 
        Matcher=elb.Matcher(HttpCode="200"), 
        Name="APPtgstatic", 
        Port="80", 
        Protocol="HTTP", 
        Targets=[ 
            elb.TargetDescription(Id=Ref(instance1a), Port="8080"), elb.TargetDescription(Id=Ref(instance1b), Port="8080") 
        ], 
        UnhealthyThresholdCount="3", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

listener = t.add_resource(
    elb.Listener(
        "Listenerstatic",
        Port="80",
        Protocol="HTTP",
        LoadBalancerArn=Ref(alb),
        DefaultActions=[
            elb.Action(Type="forward", TargetGroupArn=Ref(targetGroup))
        ]
    )
)

t.add_resource(
    elb.ListenerRule(
        "ListenerRulestatic",
        ListenerArn=Ref(listener),
        Conditions=[elb.Condition(Field="path-pattern", Values=["/*"])],
        Actions=[
            elb.ListenerRuleAction(Type="forward", TargetGroupArn=Ref(targetGroup))
        ],
        Priority="1"
    )
)

taskDefinition = t.add_resource(
    ecs.TaskDefinition(
        "taskDefinitionstatic", 
        Cpu="256", 
        Memory="512", 
        NetworkMode="host", 
        ContainerDefinitions=[
            ecs.ContainerDefinition("containerDefinition", Name="pyApp", Image=testImage)
        ], 
        Tags=tags
    )
)

service = t.add_resource(
    ecs.Service(
        "MyServicestatic",
        Cluster=Ref(ecsCluster),
        DesiredCount=2,
        TaskDefinition=Ref(taskDefinition),
        LaunchType="EC2", 
        Tags=tags 
    )
)




print(t.to_yaml())