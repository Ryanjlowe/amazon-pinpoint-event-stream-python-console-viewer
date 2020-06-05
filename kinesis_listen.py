#!/usr/bin/python

import boto3
import json
import time
import logging
import re
import sys
import getopt


if len(sys.argv) != 3:
    print('Usage: kinesis_listen.py <aws_profile_name> <kinesis_stream_name>')
    print('')
    sys.exit()

try:
    profile_name = sys.argv[1]
    stream_name = sys.argv[2]


    session = boto3.Session(profile_name=profile_name)

    client = session.client('kinesis')

    logging.getLogger().setLevel('INFO')
    logging.basicConfig(format='%(message)s')
    ip_addr_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    aws_acct_regex = re.compile(r'\"awsAccountId\": ?\"([0-9]*)\"')

    response = client.get_shard_iterator(
        StreamName = stream_name,
        ShardId = 'shardId-000000000000',
        ShardIteratorType = 'LATEST'
    )

    shard_it = response['ShardIterator']

    logging.info('Listening for messages...  Press Ctrl-C to exit')

    while 1 == 1:
        out = client.get_records(
            ShardIterator = shard_it,
            Limit = 2
        )
        shard_it = out['NextShardIterator']
        for record in out['Records']:
            d = record['Data'].decode("utf-8")
            d = re.sub(ip_addr_regex, '***.***.***.***', d)
            d = re.sub(aws_acct_regex, '"awsAccountId": "*****"', d)
            data = json.loads(d)
            logging.info('\n' + json.dumps(data, indent=4, separators=(',', ': ')))
        time.sleep(0.5)
except KeyboardInterrupt:
    print('')
