#!/usr/bin/env python

import sys
import json
import cwlproto
import yaml

wf = cwlproto.load_cwl(sys.argv[1], True)

print yaml.safe_dump(cwlproto.to_dict(wf), default_flow_style=False)
