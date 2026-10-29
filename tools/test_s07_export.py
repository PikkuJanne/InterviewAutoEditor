"""S07 mathematical and synthetic export regressions; no invented GUI origin."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from interview_auto_editor.contracts import Override
from interview_auto_editor.adapters.export import export_project, put
from interview_auto_editor.adapters.kdenlive import IntakeError
from interview_auto_editor.intake import FileMapping, MappingManifest, inspect
from interview_auto_editor.planner import GapApproval, PlannerRequest, analysis_digest, plan_pauses
from interview_auto_editor.probe import fingerprint
from interview_auto_editor.turns import build_turns, pieces
from test_s06_planner import fixture, event, request
from test_s02_adapter import semantics

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'tests/fixtures/kdenlive-26.08.2'
FFPROBE = os.environ.get('IAE_FFPROBE') or shutil.which('ffprobe')


def synthetic_result(project=FIX / 'starter-2.kdenlive'):
    """Construction-labelled tones and gaps, not inferred human turns."""
    mapping = MappingManifest(1, tuple(FileMapping(str(FIX / f'media-2/participant-{i:02}.wav'),
        f'p{i-1}', f'Participant {i:02}', (f'participant{i}',)) for i in (1, 2)), ())
    intake = inspect(project, mapping, FFPROBE)
    # Verified origins apply only to generated equal-length construction media.
    a = replace(intake.analysis, sources=tuple(replace(s, origin_status='verified', verified_offset=F(0)) for s in intake.analysis.sources))
    a = replace(a, events=(event(a, 'a1', 'p0', F(4,3), F(17,6)),
        event(a, 'b1', 'p1', F(8,3), F(25,6)),
        event(a, 'a2', 'p0', F(22,3), F(53,6)),
        event(a, 'b2', 'p1', F(26,3), F(61,6))))
    # Independent construction gaps between active tones on ALL sources.
    approvals = (GapApproval('digital-gap', F(25,6), F(22,3), 'construction_label', 'Generated PCM gap on both tracks'),)
    result = plan_pauses(a, request(a, approvals=approvals))
    bindings = {'video': FIX / 'media-2/zoom-source.mp4', 'p0': FIX / 'media-2/participant-01.wav', 'p1': FIX / 'media-2/participant-02.wav'}
    return result, bindings, {'p0': 'Participant 01', 'p1': 'Participant 02'}


class TurnTests(unittest.TestCase):
    def test_words_backchannels_and_ambiguous_events_do_not_fragment(self):
        a = fixture()
        events = tuple(event(a, f'word{i}', 'p0', F(i,5)+1, F(i,5)+F(11,10)) for i in range(15))
        a = replace(a, events=events+(event(a, 'brief', 'p1', 2, F(11,5)), event(a, 'noise', 'p1', 6, 7, 'uncertainty')))
        result = plan_pauses(a, request(a, approvals=()))
        layout = build_turns(result)
        self.assertEqual(layout.plan.edit_units, (0, 300))
        self.assertEqual([c.kind for c in layout.cues].count('turn'), 1)
        self.assertIn('backchannel', [c.kind for c in layout.cues])
        self.assertEqual(layout.plan.analysis, a)

    def test_overlap_gets_aligned_boundaries_and_retains_all_sources(self):
        a = fixture()
        a = replace(a, events=(event(a,'a','p0',1,6),event(a,'b','p1',4,9)))
        result = plan_pauses(a, request(a, approvals=()))
        layout = build_turns(result)
        self.assertEqual(layout.plan.edit_units, (0,100,150,300))
        overlap = next(c for c in layout.cues if c.kind == 'overlap')
        self.assertEqual((overlap.source_ids,overlap.source_start,overlap.source_end),(('p0','p1'),F(4),F(6)))
        self.assertEqual(sum(b-a for a,b,_ in pieces(layout.plan)),300)

    def test_shared_microphone_is_inseparable_and_guide_only(self):
        a = fixture(labels=(('a','b'),('c',)))
        a = replace(a,events=(event(a,'shared','p0',1,5),event(a,'other','p1',6,8)))
        layout = build_turns(plan_pauses(a,request(a)))
        self.assertEqual(layout.plan.edit_units,(0,300))
        self.assertIn('shared_activity',[c.kind for c in layout.cues])

    def test_source_overrides_approvals_and_tampering(self):
        a = fixture()
        a = replace(a, events=(event(a,'a','p0',1,2),event(a,'b','p1',6,8)))
        result = plan_pauses(a,request(a,overrides=(Override('p0',F(2),F(6),'keep'),)))
        layout = build_turns(result)
        self.assertEqual(layout.plan.time_map.output_frames,300)
        self.assertEqual(layout.plan.overrides,result.plan.overrides)
        bad = replace(result,plan=replace(result.plan,edit_units=(0,1,300)))
        with self.assertRaisesRegex(ValueError,'reproduce'):
            build_turns(bad)

    def test_fractional_rate_and_500_turns_no_drift(self):
        for fps in (F(25),F(30000,1001)):
            a=fixture(fps=fps,seconds=F(3003))
            a=replace(a,events=tuple(event(a,f'e{i}',f'p{i%2}',i*5+1,i*5+2) for i in range(500)))
            layout=build_turns(plan_pauses(a,request(a,approvals=())))
            self.assertEqual(len(layout.plan.edit_units),501)
            self.assertEqual(layout.plan.edit_units[-1],int(3003*fps))
            self.assertEqual(sum(b-a for a,b,_ in pieces(layout.plan)),int(3003*fps))

    def test_origins_tails_and_strict_wire_remain_refused(self):
        a=fixture()
        for changed in (replace(a.sources[1],origin_status='unverified',verified_offset=None),replace(a.sources[1],sample_count=576001,duration=F(576001,48000))):
            bad=replace(a,sources=(a.sources[0],changed,a.sources[2]))
            with self.assertRaises(ValueError):
                plan_pauses(bad,request(bad))

    def test_no_activity_and_recovery_keep_complete_handles(self):
        a=fixture()
        layout=build_turns(plan_pauses(a,request(a)))
        self.assertEqual(tuple(pieces(layout.plan)),((0,300,0),))
        a=replace(a,events=(event(a,'a','p0',2,3),event(a,'b','p1',7,8)))
        r=plan_pauses(a,request(a))
        layout=build_turns(r)
        self.assertEqual(layout.plan.time_map,r.plan.time_map)
        restored=build_turns(plan_pauses(a,request(a,overrides=(Override('p1',F(0),F(12),'keep'),))))
        self.assertEqual(restored.plan.time_map.output_frames,300)
        self.assertEqual(next(pieces(restored.plan))[0],0)
        self.assertEqual(tuple(pieces(restored.plan))[-1][1],300)

    def test_overlap_sweep_uses_raw_activity_not_joined_silence(self):
        a=fixture()
        a=replace(a,events=(event(a,'a1','p0',1,2),event(a,'a2','p0',F(5,2),4),event(a,'b','p1',F(21,10),F(12,5))))
        layout=build_turns(plan_pauses(a,request(a,approvals=())))
        self.assertFalse(any(c.kind=='overlap' for c in layout.cues))


@unittest.skipUnless(FFPROBE,'Set IAE_FFPROBE for actual media export checks.')
class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.result,self.bindings,self.names=synthetic_result()

    def export(self, **kw):
        return export_project(self.result,FIX/'starter-2.kdenlive',self.bindings,self.names,self.folder/'new.kdenlive',FFPROBE,experimental=True,**kw)

    def test_shared_export_groups_guides_bin_and_streams(self):
        before={p:fingerprint(p) for p in [FIX/'starter-2.kdenlive',*self.bindings.values()]}
        report=self.export()
        tracks,groups,guides=semantics(self.folder/'new.kdenlive')
        expected=[(pos,a,b) for a,b,pos in pieces(build_turns(self.result).plan)]
        self.assertTrue(all([e[:3] for e in entries]==expected for _,entries in tracks))
        self.assertTrue(all(len(g['children'])==3 for g in groups))
        self.assertEqual(len(groups),len(expected))
        self.assertGreater(len(guides),2)
        self.assertEqual(len(ET.parse(self.folder/'new.kdenlive').getroot().find("playlist[@id='main_bin']").findall('entry')),4)
        self.assertTrue(all(fingerprint(p)==h for p,h in before.items()))
        self.assertLess(report['output_frames'],300)
        for chain in ET.parse(self.folder/'new.kdenlive').getroot().findall('chain'):
            p={v.get('name'):v.text for v in chain.findall('property')}
            if p.get('resource','').endswith('.mp4'):
                self.assertEqual((p['audio_index'],p['astream'],p['set.test_audio']),('-1','-1','1'))

    def test_no_overwrite_optin_fingerprint_binding_and_failed_publication(self):
        self.export()
        with self.assertRaises(FileExistsError): self.export()
        with self.assertRaises(IntakeError):
            export_project(self.result,FIX/'starter-2.kdenlive',self.bindings,self.names,self.folder/'x',FFPROBE)
        for bindings,names in (({},self.names),(self.bindings,{'p0':'Same','p1':'same'})):
            with self.assertRaises(IntakeError):
                export_project(self.result,FIX/'starter-2.kdenlive',bindings,names,self.folder/'x',FFPROBE,experimental=True)
        a=replace(self.result.plan.analysis,header=replace(self.result.plan.analysis.header,project_sha256='0'*64))
        r=plan_pauses(a,request(a,approvals=()))
        with self.assertRaisesRegex(IntakeError,'FINGERPRINT'):
            export_project(r,FIX/'starter-2.kdenlive',self.bindings,self.names,self.folder/'x',FFPROBE,experimental=True)
        self.assertFalse((self.folder/'x').exists())

    def test_changed_media_and_native_extent_observation(self):
        a=self.result.plan.analysis
        changed=replace(a,sources=tuple(replace(s,sha256='0'*64) if s.source_id=='p0' else s for s in a.sources))
        r=plan_pauses(changed,request(changed,approvals=()))
        with self.assertRaisesRegex(IntakeError,'FINGERPRINT'):
            export_project(r,FIX/'starter-2.kdenlive',self.bindings,self.names,self.folder/'bad',FFPROBE,experimental=True)
        project=self.folder/'extent.kdenlive'
        root=ET.parse(FIX/'starter-2.kdenlive').getroot();root.set('root',str(FIX))
        seq=next(n for n in root.findall('tractor') if n.find("property[@name='kdenlive:sequenceproperties.groups']") is not None)
        seq.set('out','300');ET.ElementTree(root).write(project,encoding='utf-8')
        a=replace(a,header=replace(a.header,project_sha256=fingerprint(project)))
        report=export_project(plan_pauses(a,request(a,approvals=())),project,self.bindings,self.names,self.folder/'extent-output',FFPROBE,experimental=True)
        self.assertEqual(report['input_sequence_extent_delta_frames'],1)
        self.assertEqual(report['output_frames'],300)

    def test_cli_private_errors_and_exclusive_output(self):
        from interview_auto_editor.contracts import dumps
        from interview_auto_editor.intake import FileMapping,MappingManifest
        result=self.folder/'result.json';result.write_text(dumps(self.result),encoding='utf-8')
        mapping=self.folder/'mapping.json';mapping.write_text(dumps(MappingManifest(1,tuple(FileMapping(str(self.bindings[k]),k,self.names[k],(k,)) for k in ('p0','p1')),())),encoding='utf-8')
        out=self.folder/'cli.kdenlive'
        command=[sys.executable,str(ROOT/'tools/s07_export.py'),'--project',str(FIX/'starter-2.kdenlive'),'--result',str(result),'--mapping',str(mapping),'--output',str(out),'--ffprobe',str(FFPROBE),'--experimental']
        first=subprocess.run(command,capture_output=True,text=True,timeout=30)
        self.assertIn(first.returncode,(0,2),first.stderr)
        before=out.read_bytes()
        second=subprocess.run(command,capture_output=True,text=True,timeout=30)
        self.assertEqual(second.returncode,1)
        self.assertNotIn(str(self.folder),second.stderr)
        self.assertEqual(out.read_bytes(),before)

    def test_public_bundle_relocation_and_reproduction(self):
        import json
        from interview_auto_editor.contracts import loads
        from interview_auto_editor.planner import PlanningResult
        bundle=ROOT/'tests/fixtures/s07-turns-26.08.2'
        construction=json.loads((bundle/'construction.json').read_text())
        for item in construction['files']:
            self.assertEqual(fingerprint(bundle/item['path']),item['sha256'])
        moved=self.folder/'moved package ä'
        shutil.copytree(bundle,moved)
        result=loads(PlanningResult,(moved/'planning-result.json').read_text())
        bindings={'video':moved/'media/zoom-source.mp4','p0':moved/'media/participant-01.wav','p1':moved/'media/participant-02.wav'}
        target=moved/'reproduced.kdenlive'
        export_project(result,moved/'before.kdenlive',bindings,self.names,target,FFPROBE,experimental=True)
        self.assertEqual(target.read_bytes(),(bundle/'after.kdenlive').read_bytes())

    def test_n_tracks_share_every_boundary(self):
        for count in (1,3,6,8):
            root=ET.parse(FIX/'starter-2.kdenlive').getroot()
            root.set('root',str(FIX))
            nodes={n.get('id'):n for n in root if n.get('id')}
            seq=next(n for n in root.findall('tractor') if 'kdenlive:sequenceproperties.groups' in {p.get('name'):p.text for p in n.findall('property')})
            for ref in list(seq.findall('track'))[1:]:seq.remove(ref)
            for old in list(root.findall('tractor')):
                if old.get('id') not in (seq.get('id'),'tractor2') and not old.find("property[@name='kdenlive:projectTractor']") is not None:
                    root.remove(old)
            binding={'video':self.bindings['video']}; names={}; sources=[next(s for s in self.result.plan.analysis.sources if s.kind=='video')]
            for i in range(count):
                path=self.folder/f'channel {count}-{i} ä.wav';shutil.copyfile(self.bindings['p0'],path)
                identity=f'p{i}';binding[identity]=path;names[identity]=f'Channel {i}'
                sources.append(replace(next(s for s in self.result.plan.analysis.sources if s.source_id=='p0'),source_id=identity,channel_labels=(identity,)))
                chain=deepcopy(nodes['chain0']);chain.set('id',f'nchain{i}');put(chain,'resource',str(path));put(chain,'kdenlive:id',100+i);root.insert(0,chain)
                track=deepcopy(nodes['tractor0']);track.set('id',f'ntrack{i}')
                for j,f in enumerate(track.findall('filter')):f.set('id',f'nfilter{i}-{j}')
                for j,ref in enumerate(track.findall('track')):
                    pl=deepcopy(nodes[ref.get('producer')]);pl.set('id',f'npl{i}-{j}');ref.set('producer',pl.get('id'))
                    for e in pl.findall('entry'):e.set('producer',chain.get('id'));put(e,'kdenlive:id',100+i)
                    root.insert(0,pl)
                root.insert(list(root).index(seq),track);seq.insert(list(seq).index(seq.findall('track')[-1])+1,ET.Element('track',producer=track.get('id')))
            seq.insert(list(seq).index(seq.findall('track')[-1])+1,ET.Element('track',producer='tractor2'))
            project=self.folder/f'hand-authored-count-{count}.kdenlive';ET.ElementTree(root).write(project,encoding='utf-8')
            a=replace(self.result.plan.analysis,header=replace(self.result.plan.analysis.header,project_sha256=fingerprint(project)),sources=tuple(sources),events=())
            a=replace(a,events=(event(a,'left','p0',1,2),event(a,'right','p0',6,8)))
            result=plan_pauses(a,request(a))
            output=self.folder/f'count-{count}.kdenlive'
            export_project(result,project,binding,names,output,FFPROBE,experimental=True)
            tracks,groups,_=semantics(output)
            self.assertEqual(len(tracks),count+1)
            self.assertTrue(all(len(g['children'])==count+1 for g in groups))
            self.assertTrue(all([e[:3] for e in t[1]]==[e[:3] for e in tracks[0][1]] for t in tracks))
            exported=ET.parse(output).getroot()
            nodes={n.get('id'):n for n in exported if n.get('id')}
            resources={next(p.text for p in nodes[e.get('producer')].findall('property') if p.get('name')=='resource') for e in nodes['main_bin'].findall('entry') if nodes[e.get('producer')].tag=='chain'}
            self.assertTrue(all(any(Path(value).name==p.name for value in resources) for p in binding.values()))


if __name__=='__main__':unittest.main()
