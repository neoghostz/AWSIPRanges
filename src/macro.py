import json
import os
import logging
import traceback

import builder
from customerror import requiredfielderror

from typing import Union


def handler(event: dict, context: object) -> Union[dict, Exception]:
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger('Builder')
    logger.setLevel(int(os.environ.get('Logging', logging.DEBUG)))
    aws_ip_ranges_url = os.environ.get('AWSIPRangesURL', 'https://ip-ranges.amazonaws.com/ip-ranges.json')
    macro_response: dict = {
        'requestId': event.get('requestId'),
        'status': None
    }
    resources: dict = {}
    outputs: dict = {}
    response: dict = event['fragment']
    parameters: dict = event.get('templateParameterValues', {})
    try:
        for k in list(response['Resources'].keys()):
            if response['Resources'][k]['Type'] == 'ElendelOSS::Network::AWSIPranges':
                if 'Properties' in response['Resources'][k]:
                    _builder = builder.builder(k, response['Resources'][k]['Properties'], parameters, ipranges_uri=aws_ip_ranges_url)

                    _builder.build_all()
                    _template = _builder.get_template()
                    logger.debug(json.dumps(_template))
                    resources.update(_template.get('Resources'))
                    outputs.update(_template.get('Outputs'))
                    print(outputs)

        response['Resources'] = resources
        response['Outputs'] = outputs
    except requiredfielderror as e:
        logger.error(e)
        macro_response['status'] = 'failure'
        macro_response['errorMessage'] = str(e)
    except AssertionError as e:
        logger.error(e)
        logger.error(traceback.print_exc())
    except Exception as e:
        logger.error(e)
        logger.error(traceback.print_exc())
        macro_response['status'] = 'failure'
        macro_response['errorMessage'] = str(e)
    else:
        macro_response['status'] = 'success'
        macro_response['fragment'] = response
        logger.info(json.dumps(macro_response, default=str, sort_keys=True, indent=4, separators=(",", ": ")))
    finally:
        return macro_response
