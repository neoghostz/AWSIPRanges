# AWS IP Ranges

A small Cloudformation Transform to generate security groups against the IP Range list published by AWS.
It can be used as a shortcut to keep upto date with the Dynamic list, this should reduce the effort involved in keeping a Security Group against an ALB/NLB sitting behind a Cloudfront resource and ensuring the origin service can only be communicated from Cloudfront.

## Limits

So with any security group you are limited to the number of rules per group.
The seperation into a Security to each set of Region & Service should help with this.

### Number of Outputs in a Stack

The concern is always the amount of outputs per stack

So roughly \binom{n}{regions \times services} > 1 where n = 60

### Rules in a Security Group

The concern will always be with the list of rules.

So roughly \binom{n}{rules \times ipranges} > 1 where n = 100

## Security Group Rule Breakdown

```yaml
Ingress/Egress Rules: "[protocol_number|protocol_name], from_port, to_port, description"
```

## Example Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: AWS IPRanges Transform Template
Transform: "012345678912::awsipranges"
Parameters:
    VpcId:
        Type: String
        Description: VPC ID
Mappings: {}
Resources:
    WebAWSIPRanges:
        Type: ElendelOSS::Network::AWSIPranges
        Properties:
            Name: Web
            Regions:
            #- ap-northeast-1
            #- ap-northeast-2
            #- ap-northeast-3
            #- ap-south-1
            #- ap-southeast-1
            - ap-southeast-2
            #- ca-central-1
            #- cn-north-1
            #- cn-northwest-1
            #- eu-central-1
            #- eu-north-1
            #- eu-west-1
            #- eu-west-2
            #- eu-west-3
            #- me-south-1
            #- sa-east-1
            #- us-east-1
            #- us-east-2
            #- us-gov-east-1 
            #- us-gov-west-1
            #- us-west-1
            #- us-west-2
            Services:
            - AMAZON
            #- AMAZON_CONNECT
            #- CLOUD9
            - CLOUDFRONT
            #- CODEBUILD
            - EC2
            #- GLOBALACCELERATOR
            #- ROUTE53
            #- ROUTE53_HEALTHCHECKS
            #- S3
            SecurityGroupIngress:
            - [6,80,80, HTTP]
            - [6,443,443, HTTPS]
            SecurityGroupEgress:
            - [6,53,53, TCP DNS]
            - [17,53,53, UDP DNS]
            Tags:
                Purpose: IngressEdge
                Services: Amazon,Cloudfront,EC2
```
