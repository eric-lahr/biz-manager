#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BizmgrInfraStack } from '../lib/bizmgr-infra-stack';

const app = new cdk.App();
new BizmgrInfraStack(app, 'BizmgrInfraStack', {
  env: { account: '186391590807', region: 'us-west-2' },
});