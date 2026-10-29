#!/usr/bin/env python3
"""S06 offline plan from a local v1 analysis and explicit gap approvals.

Writes one new private planning-result JSON. No project export or inference.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interview_auto_editor.contracts import Analysis, dumps, loads
from interview_auto_editor.planner import PlannerRequest, plan_pauses
from interview_auto_editor.speech import atomic_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('analysis', 'request', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('Output exists.')
        with args.analysis.open(encoding='utf-8') as stream:
            analysis = loads(Analysis, stream.read(8 * 1024 * 1024 + 1))
        with args.request.open(encoding='utf-8') as stream:
            request = loads(PlannerRequest, stream.read(8 * 1024 * 1024 + 1))
        result = plan_pauses(analysis, request)
        atomic_new(args.output, dumps(result))
    except KeyboardInterrupt:
        parser.exit(130, 'S06 cancelled. Sources unchanged.\n')
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        parser.exit(1, 'S06 planning refused; inspect local contracts, origins, tails and approvals privately.\n')
    print('Shared plan written; source media unchanged. No project exported.')
    return 2 if result.plan.reviews else 0


if __name__ == '__main__':
    raise SystemExit(main())
