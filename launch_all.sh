#!/usr/bin/env bash

# kill anything on the three ports (port used by the app)
for p in 5001 8000 8010; do
  lsof -ti tcp:$p | xargs -r kill -9
done

# start both launchers from their own folders
(cd ensembl-mcp && ./launch.sh) &
(cd visualizer  && ./launch.sh)
