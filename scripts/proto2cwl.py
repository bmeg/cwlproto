#!/usr/bin/env python

import sys
import json
import cwlproto
import yaml

wf = cwlproto.load_proto(sys.argv[1])

print yaml.safe_dump(cwlproto.to_cwl(wf), default_flow_style=False)
