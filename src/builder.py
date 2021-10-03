#!/usr/bin/python3
import os
import logging
from customerror import requiredfielderror
from decorators import func_call_logger
from typing import Union
from awsipranges import AWSIPRanges
from troposphere import FindInMap, GetAtt, Join, Output, Not, Equals, Select, And, Or, Sub, Export, If, Parameter, Ref, Tags, Template, Condition
from troposphere.ec2 import SecurityGroup, SecurityGroupRule
from typing import Union

class builder():
    def __init__(self, name: str, properties: dict, parameters: dict, ipranges_uri: str):
        self.name = self.cloudformation_safe_string(name)
        self.awsipranges = AWSIPRanges()
        self.template = Template()
        self.template.set_version('2010-09-09')
        self.ipranges_uri = ipranges_uri
        self.resources = {}
        self.outputs = {}
        self.properties = properties
        self.parameters = parameters
        logging.basicConfig(format='%(asctime)s [%(levelname)s] (%(funcName)s) %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        self.logger = logging.getLogger('Builder.builder')
        self.logger.setLevel(int(os.environ.get('Logging', logging.DEBUG)))
        self.required_keys = ('Name', 'Regions', 'Services')
        self.required_parameters = ('VpcId')
        self.validate_network_awsipranges_obj()
        self.validate_params_obj()

    def validate_network_awsipranges_obj(self) -> Union[None, Exception]:
        if any([key for key in self.required_keys if key not in self.properties.key()]):
            raise requiredfielderror(f'Missing Properties: {any([key for key in self.required_keys if key not in self.properties.key()])}')

    def validate_params_obj(self) -> Union[None, Exception]:
        if any([key for key in self.required_parameters if key not in self.parameters.key()]):
            raise requiredfielderror(f'Missing Parameters: {any([key for key in self.required_parameters if key not in self.parameters.key()])}') 

    def cloudformation_safe_string(self, unsafe_string: str) -> str:
        if isinstance(unsafe_string, str):
            unsafe_char = '!@#$%^&*()_'
            safe_string_list = [x for x in unsafe_string if x not in unsafe_char]

            return str(''.join(safe_string_list))
        else:
            raise TypeError('CFN Object Name is not a String')

    def str_2_bool(self, v: bool) -> bool:
        if isinstance(v, bool):
            return v
        else:
            if v.lower() in ('yes', 'true', 't', '1'):
                return True
            else:
                return False

    def build_troposphere_tags(self, name: str, tags: dict) -> dict:
        tags["Name"] = name

        return tags


    def get_template(self) -> dict:
        self.logger.debug('Calling Get Template')
        return self.template.to_dict()

    @func_call_logger
    def build_all(self) -> None:
        self.awsipranges.get_aws_ip_ranges_payload()
        self.awsipranges.parse_ip_ranges()
        filtered_aws_ip_ranges: list = self.awsipranges.by_service
        self.build_securitygroup(filtered_aws_ip_ranges)

    @func_call_logger
    def build_securitygroup(self, filtered_aws_ip_ranges: dict):
        try:
            self.template.add_resource(
                SecurityGroup(
                    f"{self.cloudformation_safe_string(self.properties['Name'])}",
                    GroupName=self.cloudformation_safe_string(self.properties['Name']),
                    GroupDescription=f"Sec Group: {self.cloudformation_safe_string(self.properties['Name'])} built by AWSIPRanges",
                    VpcId=Ref(f"{self.parameters['VpcId']}"),
                    Tags=Tags(self.build_troposphere_tags(self.cloudformation_safe_string(self.properties['Name']), self.properties.get("Tags", {}))),
                    SecurityGroupEgress=build_security_group_rules(self.properties.get('SecurityGroupEgress', []), filtered_aws_ip_ranges),
                    SecurityGroupIngress=build_security_group_rules(self.properties.get('SecurityGroupIngress', []), filtered_aws_ip_ranges)
                )
            )
        except AssertionError as e:
            self.logger.error(f"Failure to add Security Group {self.cloudformation_safe_string(self.properties['Name'])} resource")
        else:
            self.logger.debug(f"Successfully added Security Group {self.cloudformation_safe_string(self.properties['Name'])} resource")

    @func_call_logger
    def build_security_group_rules(self, group_rules: list, aws_ip_ranges: list) -> list:
        rules_list: list = []
        for ip in aws_ip_ranges:
            for rule in group_rules:
                rules_list.append(
                    SecurityGroupRule(
                        IpProtocol=rule[0],
                        FromPort=rule[1],
                        ToPort=rule[2],
                        CidrIp=ip,
                        Description=rule[3]
                    )
                )

        return rules_list

    @func_call_logger
    def filter_ip_ranges(self, aws_ip_ranges) -> list:
        filtered_ipranges = [aws_ip_ranges[service][region] for service in aws_ip_ranges.keys() if service in self.properties['Services'] for region in aws_ip_ranges[service].keys() if region in self.properties['Regions']]

        return filtered_ipranges
