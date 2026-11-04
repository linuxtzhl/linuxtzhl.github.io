#!/usr/bin/env python3
import sys
join = []
key = []
total = len(sys.argv)
args = sys.argv[1:total]
def testing():
    for arg in args:
        if arg == "kubeadm":
            join.extend(args[0:5])
        elif "--discovery" in arg:
            key.append(arg[1:])
        elif "sha256" in arg:
            key.append(arg)
    print(' '.join(join+key))

testing()