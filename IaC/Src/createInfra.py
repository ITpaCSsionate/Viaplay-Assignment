from troposphere import Ref, Template, Base64, Join, GetAtt, Tags
import troposphere.ec2 as ec2 
import troposphere.ecs as ecs
import troposphere.elasticloadbalancingv2 as elb
from troposphere.iam import InstanceProfile, PolicyType, Role
import troposphere.autoscaling as autoscaling
import troposphere.autoscalingplans as autoscalingplans
import json

configuration = json.load(open("../Configuration/Configuration.json", 'r'))
tagsC = configuration["tags"]
tags = Tags(tagsC)
tagsAutoScaling = []
for k,v in tagsC.items():
    tagsAutoScaling.append(autoscaling.Tag(k,v,True))
region = configuration["region"]
ecsClusterName = configuration["ecsClusterName"]
serviceName = configuration["serviceName"]
testImage = configuration["dockerImage"]
keyNames = configuration["keyNames"]

t = Template()


vpc = t.add_resource(
    ec2.VPC(
        "ViaPlayTest", 
        CidrBlock="10.2.0.0/16", 
        EnableDnsHostnames=True, 
        EnableDnsSupport=True, 
        Tags=tags
    )
)

subnet1a = t.add_resource(
    ec2.Subnet(
        "PrivateSubnet1a", 
        CidrBlock="10.2.0.0/18", 
        AvailabilityZone="eu-west-1a", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

subnet1b = t.add_resource(
    ec2.Subnet(
        "PrivateSubnet1b", 
        CidrBlock="10.2.64.0/18", 
        AvailabilityZone="eu-west-1b", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

subnet1c = t.add_resource(
    ec2.Subnet(
        "PrivateSubnet1c", 
        CidrBlock="10.2.128.0/18", 
        AvailabilityZone="eu-west-1c", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

subnetAdministration1a = t.add_resource(
    ec2.Subnet(
        "Administration1a", 
        CidrBlock="10.2.192.0/19", 
        AvailabilityZone="eu-west-1a", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)
subnetAdministration1b = t.add_resource(
    ec2.Subnet(
        "Administration1b", 
        CidrBlock="10.2.224.0/19", 
        AvailabilityZone="eu-west-1b", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

vpcIngressTCP = ec2.SecurityGroupRule("ingressTCP", IpProtocol="tcp", FromPort="0", ToPort="65535", CidrIp="10.2.0.0/16")
vpcIngressUDP = ec2.SecurityGroupRule("ingressUDP", IpProtocol="udp", FromPort="0", ToPort="65535", CidrIp="10.2.0.0/16")

vpcEgressTCP = ec2.SecurityGroupRule("egressTCP", IpProtocol="tcp", FromPort="0", ToPort="65535", CidrIp="0.0.0.0/0")
vpcEgressUDP = ec2.SecurityGroupRule("egressUDP", IpProtocol="udp", FromPort="0", ToPort="65535", CidrIp="0.0.0.0/0")

HTTPIngress = ec2.SecurityGroupRule("ingressTCP", IpProtocol="tcp", FromPort="80", ToPort="80", CidrIp="0.0.0.0/0")

allowAllIntheSubnetSG = t.add_resource(
    ec2.SecurityGroup(
        "generalSG", 
        GroupDescription="allows everything in the private subnet", 
        SecurityGroupIngress=[vpcIngressTCP, vpcIngressUDP], 
        VpcId=Ref(vpc), 
        SecurityGroupEgress=[vpcEgressTCP, vpcEgressUDP], 
        Tags=tags
    )
)


ecsAgentEndpoint = t.add_resource(
    ec2.VPCEndpoint(
        "ecsAgent", 
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
        "ecsTelemetry", 
        VpcEndpointType="Interface", 
        PrivateDnsEnabled=True, 
        ServiceName="com.amazonaws.eu-west-1.ecs-telemetry", 
        VpcId=Ref(vpc), SubnetIds=[Ref(subnet1a), Ref(subnet1b), Ref(subnet1c)], 
        SecurityGroupIds=[GetAtt(allowAllIntheSubnetSG, "GroupId")]
    )
)

ecsEndpoint = t.add_resource(
    ec2.VPCEndpoint(
        "ecs", 
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
        "ecrApi", 
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
        "ecrDkr", 
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
        "IGW", 
        Tags=tags
    )
)

internetGatewayAttachment = t.add_resource(
    ec2.VPCGatewayAttachment(
        "igwA", 
        InternetGatewayId=Ref(internetGateway), 
        VpcId=Ref(vpc)
    )
)

routeTableAdministration = t.add_resource(
    ec2.RouteTable(
        "RTadministration", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)


routeAdminstration = t.add_resource(
    ec2.Route(
        "routeAdministration", 
        DestinationCidrBlock="0.0.0.0/0", 
        GatewayId=Ref(internetGateway), 
        RouteTableId=Ref(routeTableAdministration)
    )
)

## Reference: https://aws.amazon.com/premiumsupport/knowledge-center/public-load-balancer-private-ec2/
routeTableAdministrationAssociation1a = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "adminrtassoc1a", 
        RouteTableId=Ref(routeTableAdministration), 
        SubnetId=Ref(subnetAdministration1a)
    )
)

routeTableAdministrationAssociation1b = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "adminrtassoc1b", 
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
    "sshIngress", 
    IpProtocol="tcp", 
    FromPort="22", 
    ToPort="22", 
    CidrIp="0.0.0.0/0"
)

bastionInstanceSG = t.add_resource(
    ec2.SecurityGroup(
        "bastionInstanceSG", 
        GroupDescription="sg for nat gw instance", 
        SecurityGroupIngress=[vpcIngressTCP, vpcIngressUDP, sshIngress], 
        VpcId=Ref(vpc), 
        SecurityGroupEgress=[vpcEgressTCP, vpcEgressUDP], 
        Tags=tags
    )
)


bastionInstance = t.add_resource(
    ec2.Instance(
        "bastionInstance", 
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
        "bastionInstanceEIP", 
        InstanceId=Ref(bastionInstance), 
        Tags=tags
    )
)

elasticIpAssociation = t.add_resource(
    ec2.EIPAssociation(
        "bastionInstanceEIPAssociation", 
        EIP=Ref(elasticIp), 
        InstanceId=Ref(bastionInstance)
    )
)

routeTable = t.add_resource(
    ec2.RouteTable(
        "routeTable", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

s3Endpoint = t.add_resource(
    ec2.VPCEndpoint(
        "S3", 
        VpcEndpointType="Gateway", 
        ServiceName="com.amazonaws.eu-west-1.s3", 
        VpcId=Ref(vpc), 
        RouteTableIds=[Ref(routeTableAdministration), Ref(routeTable)]
    )
)

routeTable1aAssociation = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "1artassoc", 
        RouteTableId=Ref(routeTable), 
        SubnetId=Ref(subnet1a)
    )
)

routeTable1bAssociation = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "1brtassoc", 
        RouteTableId=Ref(routeTable), 
        SubnetId=Ref(subnet1b)
    )
)

routeTable1cAssociation = t.add_resource(
    ec2.SubnetRouteTableAssociation(
        "1crtassoc", 
        RouteTableId=Ref(routeTable), 
        SubnetId=Ref(subnet1c)
    )
)




EcsClusterRole = t.add_resource(
    Role(
        "EcsClusterRole",
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
        "PolicyEcs",
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
        "PolicyEcr",
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
        "EC2InstanceProfile",
        Path="/",
        Roles=[Ref(EcsClusterRole)]
    )
)

ecsCluster = t.add_resource(
    ecs.Cluster(ecsClusterName, ClusterName=ecsClusterName, Tags=tags)
)


userData = Base64(Join("", ["#!/bin/bash\necho ECS_CLUSTER=", Ref(ecsCluster), " >> /etc/ecs/ecs.config"]))
instanceTemplate = t.add_resource(
    autoscaling.LaunchConfiguration(
        "InstanceTemplate", 
        ImageId="ami-0e592a261c043bc6a", 
        InstanceType="t2.micro", 
        SecurityGroups=[Ref(allowAllIntheSubnetSG)], 
        KeyName=keyNames[0], 
        UserData=userData,
        IamInstanceProfile=Ref(EC2InstanceProfile)
    )
)


autoscalingGroup = t.add_resource(
    autoscaling.AutoScalingGroup(
        "AutoScalingGroup",
        AutoScalingGroupName="ECSInstances",
        LaunchConfigurationName=Ref(instanceTemplate),
        AvailabilityZones=["eu-west-1a","eu-west-1b"],
        DesiredCapacity="2",
        MinSize="2",
        MaxSize="3",
        #DependsOn=,
        VPCZoneIdentifier=[Ref(subnet1a), Ref(subnet1b)],
        Tags=tagsAutoScaling
    )
)

autoscalingPolicy = t.add_resource(
    autoscaling.ScalingPolicy(
        "scalingPolicy",
        PolicyType="TargetTrackingScaling",
        AutoScalingGroupName=Ref(autoscalingGroup),
        AdjustmentType="ChangeInCapacity",
        TargetTrackingConfiguration=autoscaling.TargetTrackingConfiguration(
            "trackCFG", TargetValue=60, PredefinedMetricSpecification=autoscaling.PredefinedMetricSpecification(PredefinedMetricType="ASGAverageCPUUtilization")
        )
    )
)


allowHTTPSG = t.add_resource(
    ec2.SecurityGroup(
        "AllowHTTP", 
        GroupDescription="AllowHTTP", 
        SecurityGroupIngress=[HTTPIngress], 
        VpcId=Ref(vpc), 
        SecurityGroupEgress=[vpcEgressTCP, vpcEgressUDP], 
        Tags=tags
    )
)


alb = t.add_resource(
    elb.LoadBalancer(
        "ViaPlayAssignmentLB", 
        Name="ViaPlayAssignment", 
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
        "APPtg", 
        HealthCheckIntervalSeconds="30", 
        HealthCheckPath="/healthz", 
        HealthCheckProtocol="HTTP", 
        HealthCheckTimeoutSeconds="10", 
        HealthyThresholdCount="4", 
        Matcher=elb.Matcher(HttpCode="200"), 
        Name="APPtg", 
        Port="80", 
        Protocol="HTTP", 
        UnhealthyThresholdCount="3", 
        VpcId=Ref(vpc), 
        Tags=tags
    )
)

listener = t.add_resource(
    elb.Listener(
        "Listener",
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
        "ListenerRule",
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
        "taskDefinition", 
        Cpu="256", 
        Memory="512", 
        NetworkMode="bridge", 
        ContainerDefinitions=[
            ecs.ContainerDefinition("containerDefinition", Name="pyApp", Image=testImage, PortMappings=[ecs.PortMapping(ContainerPort=8080, Protocol="tcp")])
        ], 
        Tags=tags
    )
)



serviceTags = Tags({"toBeAutoscaled": "yes"})
service = t.add_resource(
    ecs.Service(
        "MyService",
        ServiceName=serviceName,
        Cluster=Ref(ecsCluster),
        DependsOn="Listener",
        DesiredCount=2,
        TaskDefinition=Ref(taskDefinition),
        LaunchType="EC2",
        LoadBalancers=[ecs.LoadBalancer(TargetGroupArn=Ref(targetGroup), ContainerName="pyApp", ContainerPort=8080)], 
        Tags=serviceTags 
    )
)



serviceScalability = t.add_resource(
    autoscalingplans.ScalingPlan(
        "autoscalingplan", 
        DependsOn="MyService",
        ApplicationSource=autoscalingplans.ApplicationSource(TagFilters=[autoscalingplans.TagFilter(Key="ToBeAutoscaled", Values=["yes"])]),
        ScalingInstructions=[
            autoscalingplans.ScalingInstruction(
                MinCapacity=2,
                MaxCapacity=4, 
                ResourceId="service/" + ecsClusterName +"/" + serviceName,
                ScalableDimension="ecs:service:DesiredCount",
                ServiceNamespace="ecs",
                TargetTrackingConfigurations=[
                    autoscalingplans.TargetTrackingConfiguration(
                        TargetValue=60, 
                        PredefinedScalingMetricSpecification=autoscalingplans.PredefinedScalingMetricSpecification(PredefinedScalingMetricType="ECSServiceAverageCPUUtilization")
                    )
                ]
            )
        ]
    )
)


print(t.to_yaml())