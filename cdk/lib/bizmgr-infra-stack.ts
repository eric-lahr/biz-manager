import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';

export class BizmgrInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    
    const natGatewayProvider = ec2.NatProvider.instance({
      instanceType: new ec2.InstanceType('t3a.nano'),
    });

    const vpc = new ec2.Vpc(this, 'Vpc', {
      ipAddresses: ec2.IpAddresses.cidr('172.16.0.0/19'),
      createInternetGateway: true,
      enableDnsHostnames: true,
      enableDnsSupport: true,
      maxAzs: 3,
      natGatewayProvider: natGatewayProvider,
      natGateways: 1,
      restrictDefaultSecurityGroup: true,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        }
     ],
     gatewayEndpoints: { // This allows access to DynamoDB & S3 without the use of NAT.
        S3: {
          service: ec2.GatewayVpcEndpointAwsService.S3,
        },
        DYNAMODB: {
          service: ec2.GatewayVpcEndpointAwsService.DYNAMODB,
        },
      }
    })

    // Your Security Groups can be defined here
    const rdsSecurityGroup = new ec2.SecurityGroup(this, 'DB', {
      vpc,
      description: 'SG for RDS',
      allowAllOutbound: false,
      disableInlineRules: true
    });
    // rdsSecurityGroup.addIngressRule(ec2.Peer.ipv4('1.1.1.1/32'), ec2.Port.tcp(3306), 'MySQL from an explicit external address');


    const deployerSecurityGroup = new ec2.SecurityGroup(this, 'Deployer', {
      vpc,
      description: 'SG for the Deployer (Zappa internal stuff etc)',
      allowAllOutbound: true,
      disableInlineRules: true
    });
    rdsSecurityGroup.addIngressRule(deployerSecurityGroup, ec2.Port.tcp(3306), 'MySQL From Deployer SG')

    const lambdaOpenSecurityGroup = new ec2.SecurityGroup(this, 'LambdaAppOpen', {
      vpc,
      description: 'SG for Lambda functions, allows internet & RDS',
      allowAllOutbound: true,
      disableInlineRules: true
    });
    rdsSecurityGroup.addIngressRule(lambdaOpenSecurityGroup, ec2.Port.tcp(3306), 'MySQL From Lambda Open SG')
    lambdaOpenSecurityGroup.addEgressRule(rdsSecurityGroup, ec2.Port.tcp(3306), 'MySQL to RDS SG') // Not directly needed as we allow all egress here, but we'll add explicitly nonetheless
    
    const lambdaClosedSecurityGroup = new ec2.SecurityGroup(this, 'LambdaAppClosed', {
      vpc,
      description: 'SG for Lambda functions, RDS only',
      allowAllOutbound: false,
      disableInlineRules: true
    });
    rdsSecurityGroup.addIngressRule(lambdaClosedSecurityGroup, ec2.Port.tcp(3306), 'MySQL From Lambda Closed SG')
    lambdaClosedSecurityGroup.addEgressRule(rdsSecurityGroup, ec2.Port.tcp(3306), 'MySQL to RDS SG')

    // RDS
    const dbInstance = new rds.DatabaseInstance(this, "db", {
      engine: rds.DatabaseInstanceEngine.MARIADB,
      // Generate the secret with admin username `postgres` and random password
      credentials: rds.Credentials.fromGeneratedSecret('postgres'),
      vpc,
      allocatedStorage: 20,
      allowMajorVersionUpgrade: false,
      autoMinorVersionUpgrade: true,
      availabilityZone: 'us-west-2a',
      backupRetention: cdk.Duration.days(5),
      port: 3306,
      removalPolicy: cdk.RemovalPolicy.SNAPSHOT,
      storageType: rds.StorageType.GP3,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      publiclyAccessible: false, // This means your instance is NOT given a public IPv4 address
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.MICRO),
      storageEncrypted: true,
      securityGroups: [
        rdsSecurityGroup
      ]
    });

  }
}
