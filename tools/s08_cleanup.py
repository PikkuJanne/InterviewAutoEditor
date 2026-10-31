#!/usr/bin/env python3
"""Create a new approved-idle cleanup result; no inference or media mutation."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.cleanup import CleanupRequest, build_cleanup
from interview_auto_editor.contracts import dumps, loads
from interview_auto_editor.planner import PlanningResult
from interview_auto_editor.speech import atomic_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('result', 'request', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = loads(PlanningResult, args.result.read_text(encoding='utf-8'))
        request = loads(CleanupRequest, args.request.read_text(encoding='utf-8'))
        cleanup = build_cleanup(result, request)
        atomic_new(args.output, dumps(cleanup))
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, TypeError):
        parser.exit(1, 'S08 cleanup refused; inspect private inputs and use a new destination.\n')
    print(f'S08 cleanup: {len(cleanup.spans)} approved spans; {len(cleanup.diagnoses)} retained approvals.')
    return 2 if cleanup.diagnoses or result.plan.reviews else 0


if __name__ == '__main__':
    raise SystemExit(main())
