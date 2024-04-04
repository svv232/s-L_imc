import sys
from json import loads

fname = sys.argv[1]
with open(fname, 'r') as f:
    buffer = ""
    for line in f:
      if line.startswith("{"):
        buffer = line

        for line in f:
          buffer += line
          if line.startswith("}"):
            break

        data = loads(buffer)
        print(data["lambdaLog"])