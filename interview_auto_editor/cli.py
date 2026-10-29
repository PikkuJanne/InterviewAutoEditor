"""Verified local CLI; console output contains no user data or private paths."""
import argparse
from pathlib import Path
import sys

from .application import Application, RunError, RunOptions, json_text
from .speech import atomic_new


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'analyze', 'plan', 'export', 'run'):
        cmd = commands.add_parser(name)
        for flag in ('project', 'mapping', 'ffprobe', 'output'):
            cmd.add_argument('--' + flag, type=Path, required=True)
        for flag in ('analysis', 'request', 'picture', 'picture-request', 'cleanup-request',
                     'ffmpeg', 'speech-model', 'reaction-model', 'cache'):
            cmd.add_argument('--' + flag, type=Path)
        cmd.add_argument('--preset', choices=('tight', 'gentle'))
        cmd.add_argument('--experimental', action='store_true')
        cmd.add_argument('--resume', action='store_true')
        cmd.add_argument('--cancel-file', type=Path, help='Presence requests cooperative cancellation; never created or removed by the service.')
    report = commands.add_parser('report')
    report.add_argument('--run', type=Path, required=True)
    probe = commands.add_parser('compatibility-probe')
    probe.add_argument('--project', type=Path, required=True)
    probe.add_argument('--output', type=Path, required=True, help='New structural probe report; no installed-build certification.')
    args = parser.parse_args(argv)
    try:
        if args.command == 'report':
            manifest = Application.report(args.run)
            print(json_text({'schema_version': 1, 'command': manifest.command,
                'state': manifest.state, 'stage': manifest.stage, 'attempt': manifest.attempt,
                'artifacts_verified': len(manifest.artifacts),
                'validation': 'Historical run artifacts only; sources not revalidated.'}), end='')
            return 2 if manifest.state == 'complete' else 1
        if args.command == 'compatibility-probe':
            result = Application().compatibility_probe(args.project)
            atomic_new(args.output, json_text(result))
            print('Structural compatibility report written; actual application testing was not performed.')
            return 2 if result['compatibility'] == 'EXPERIMENTAL' else 1
        options = RunOptions(**{k: v for k, v in vars(args).items()
                                if k not in ('resume', 'cancel_file')})
        app = Application(cancel=lambda: bool(args.cancel_file and args.cancel_file.exists()),
                          progress=lambda stage: print('Stage: ' + stage, flush=True))
        app.run(options, resume=args.resume)
        print('Run completed atomically. Review the private report; compatibility remains EXPERIMENTAL.')
        return 2  # completion with required review, never an alignment certificate
    except KeyboardInterrupt:
        print('Cancelled. No partial final run. Completed caches and staging evidence remain local.', file=sys.stderr)
        return 130
    except RunError as exc:
        print('Run refused: ' + str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError, KeyError, StopIteration, OverflowError):
        print('Run failed. Check private inputs, models, tools, approvals and staging manifest locally. Originals unchanged.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
