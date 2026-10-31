"""Local CLI. Ordinary edit reports local paths; legacy diagnostics stay neutral."""
import argparse
from pathlib import Path
import sys
from fractions import Fraction

from .application import Application, RunError, RunOptions, json_text
from .speech import atomic_new
from .editing import EditError, Mute, local_asset


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'analyze', 'plan', 'export', 'run', 'edit'):
        cmd = commands.add_parser(name)
        for flag in ('project', 'mapping', 'ffprobe', 'output'):
            cmd.add_argument('--' + flag, type=Path, required=name != 'edit' or flag in ('project', 'output'))
        for flag in ('analysis', 'request', 'picture', 'picture-request', 'cleanup-request',
                     'ffmpeg', 'speech-model', 'reaction-model', 'cache'):
            cmd.add_argument('--' + flag, type=Path)
        cmd.add_argument('--preset', choices=('tight', 'gentle'))
        cmd.add_argument('--experimental', action='store_true')
        cmd.add_argument('--target-kdenlive', type=Path, help='Read-only executable identity check against the exact tested matrix.')
        cmd.add_argument('--resume', action='store_true')
        cmd.add_argument('--cancel-file', type=Path, help='Presence requests cooperative cancellation; never created or removed by the service.')
        cmd.add_argument('--mute', nargs=3, action='append', default=[], metavar=('PARTICIPANT_ID', 'START_SECONDS', 'END_SECONDS'),
                         help='Explicit reversible mute in original-source seconds; repeat for additional noises.')
    report = commands.add_parser('report')
    report.add_argument('--run', type=Path, required=True)
    probe = commands.add_parser('compatibility-probe')
    probe.add_argument('--project', type=Path, required=True)
    probe.add_argument('--target-kdenlive', type=Path)
    probe.add_argument('--output', type=Path, required=True, help='New capability/build-identity report. Does not operate the editor.')
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
            result = Application().compatibility_probe(args.project, args.target_kdenlive)
            atomic_new(args.output, json_text(result))
            print('Compatibility: ' + result['compatibility'] + '. Report written; editor was not operated by this probe.')
            return {'TESTED': 0, 'EXPERIMENTAL': 2, 'UNSUPPORTED': 1}[result['compatibility']]
        values = {k: v for k, v in vars(args).items() if k not in ('resume', 'cancel_file', 'mute')}
        values['mutes'] = tuple(Mute(identity, Fraction(a), Fraction(b)) for identity, a, b in args.mute)
        if args.command == 'edit':
            for name in ('ffprobe', 'ffmpeg', 'speech_model', 'reaction_model', 'cache'):
                values[name] = values[name] or local_asset(name)
            # An explicit edit command selects the documented experimental path.
            values['experimental'] = True
            if args.analysis:
                # Reuse exact source-bound analysis without requiring models.
                values['speech_model'] = values['reaction_model'] = values['cache'] = None
        options = RunOptions(**values)
        app = Application(cancel=lambda: bool(args.cancel_file and args.cancel_file.exists()),
                          progress=lambda stage: print('Stage: ' + stage, flush=True))
        app.run(options, resume=args.resume)
        if args.command == 'edit':
            print('Ready project: ' + str((options.output / 'project.kdenlive').absolute()))
            print('Compatibility: ' + app.compatibility_probe(options.project, options.target_kdenlive)['compatibility'] + '. Original timing and uncertain audio are preserved.')
            return 0
        print('Run completed atomically. Review the private report for exact target compatibility.')
        return 0 if (options.target_kdenlive is not None and
            app.compatibility_probe(options.project, options.target_kdenlive)['compatibility'] == 'TESTED') else 2
    except KeyboardInterrupt:
        print('Cancelled. No partial final run. Completed caches and staging evidence remain local.', file=sys.stderr)
        return 130
    except RunError as exc:
        print('Run refused: ' + str(exc), file=sys.stderr)
        return 1
    except EditError as exc:
        print('Edit refused: ' + str(exc), file=sys.stderr)
        if args.command == 'edit':
            print('Affected starter: ' + str(args.project.absolute()), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError, KeyError, StopIteration, OverflowError, ZeroDivisionError) as exc:
        if args.command == 'edit':
            print('Edit failed for starter: ' + str(args.project.absolute()), file=sys.stderr)
            affected = getattr(exc, 'affected_input', None) or getattr(exc, 'filename', None)
            if affected:
                print('Affected input: ' + str(affected), file=sys.stderr)
            print('Check its media references and local tools/models. Preserve the incomplete run; restore missing inputs and use --resume, or choose a new output folder after changing inputs.', file=sys.stderr)
        else:
            print('Run failed. Check private inputs, models, tools, approvals and staging manifest locally. Originals unchanged.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
