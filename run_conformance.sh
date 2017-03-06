#!/bin/bash

BDIR="$(cd `dirname $0`; pwd)"

if [ ! -e common-workflow-language ]; then
  git clone https://github.com/common-workflow-language/common-workflow-language.git
fi

if [ ! -e venv ]; then
  virtualenv venv
  venv/bin/pip install cwltool supervisor pyyaml
fi

source venv/bin/activate

if [ -n "$1" ]; then
    TEST=-n$1
fi

pushd common-workflow-language
#./run_test.sh RUNNER=$BDIR/test/funnel-local-tes DRAFT=v1.0
./run_test.sh $TEST RUNNER=$BDIR/scripts/proto-test-runner DRAFT=v1.0
popd
