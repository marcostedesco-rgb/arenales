#!/bin/bash
export NODES_EXCLUDE="[]"
export N8N_BLOCK_ENV_ACCESS_IN_NODE=false
export N8N_RESTRICT_FILE_ACCESS_TO="$HOME/arenales"
npx n8n
