#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys
import tempfile
import cProfile

# initial error handling begins
# missing cprofilev
try:
    import cprofilev
except ImportError as exc:
    sys.stderr.write(('error: python package "cprofilev" not found\n'))
    sys.exit(1)

# no script given
if len(sys.argv) != 2:
    sys.stderr.write(('error: no python script given\n'))
    sys.exit(1)

# script does not exist
script_path = os.path.abspath(os.path.realpath(
    os.path.expanduser(sys.argv[1])
))
if not os.path.isfile(script_path):
    sys.stderr.write((
        'error: file "{script_path}" not found\n'
    ).format(**locals()))
    sys.exit(1)

# actual profiling begins
# build temporary profile store
(_, profile_store) = tempfile.mkstemp(
    prefix=('{0}_').format(os.path.basename(script_path)),
    suffix='.pyprofile'
)
sys.stdout.write((
    '... created profile store at "{profile_store}"\n'
).format(**locals()))

# begin profiling
sys.stdout.write((
    '... starting profiling of script "{script_path}"\n'
).format(**locals()))
with open(script_path, 'r') as fp:
    cProfile.run(fp.read(), profile_store)
sys.stdout.write((
    '... finished profiling of script "{script_path}"\n'
).format(**locals()))

# open profile view
sys.stdout.write((
    '... starting profile view server at <http://localhost:4000/>\n'
))
cprofilev.CProfileV(profile_store, script_path).start()
sys.stdout.write((
    '... killing profile view server at <http://localhost:4000/>\n'
))
sys.exit(0)
