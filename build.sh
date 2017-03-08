#!/bin/bash

if [ ! -e venv ]; then
  virtualenv venv
  . venv/bin/activate
  pip install cwltool jinja2
fi

if [ ! -e common-workflow-language ]; then  
  git clone https://github.com/common-workflow-language/common-workflow-language.git
fi

. venv/bin/activate


python -mschema_salad --print-avro ./common-workflow-language/v1.0/CommonWorkflowLanguage.yml > cwl.avsc
./scripts/cwl-avro-to-proto.py cwl.avsc > cwl.proto
protoc --python_out cwlproto cwl.proto
