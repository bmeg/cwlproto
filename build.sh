#!/bin/bash

python -mschema_salad --print-avro ./common-workflow-language/v1.0/CommonWorkflowLanguage.yml > cwl.avsc
./scripts/cwl-avro-to-proto.py cwl.avsc > cwl.proto
protoc --python_out cwlproto cwl.proto
