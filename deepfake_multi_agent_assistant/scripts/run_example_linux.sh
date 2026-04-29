#!/usr/bin/env bash
set -e

python -m deepfake_agent_assistant.cli run \
  --task-file examples/sample_task.md \
  --literature examples/sample_paper_notes.md \
  --code examples/sample_model_code.py \
  --results examples/sample_results.csv \
  --provider mock \
  --output-dir outputs/mock_demo
