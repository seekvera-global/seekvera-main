"""A provider failure must survive checkpointing as a failed process."""
import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import build_current_locale_delta as builder

class ResumeTests(unittest.TestCase):
 def run_build(self,fail):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'docs').mkdir();(root/'i18n-r32').mkdir();stage=root/'stage'
   source='A public interface sentence.';source_hash=builder.hashlib.sha256(source.encode()).hexdigest()[:16]
   (root/'i18n-r32-source.json').write_text(json.dumps({'strings':[]}));(root/'i18n-r32/manifest.json').write_text(json.dumps({'languages':['fr']}));(root/'i18n-r32/fr.json').write_text(json.dumps({'translations':{}}));(root/'docs/public-ui-translation-provenance.json').write_text(json.dumps({'publicRepository':True,'mismatches':[],'sourceHash':source_hash,'publicBlobHashes':{}}))
   def translate(*args):
    if fail:raise RuntimeError('all_translation_backends_unavailable')
    return ['Une phrase publique de l’interface.'],'test-provider'
   with patch.object(builder,'ROOT',root),patch.object(builder,'source_inventory',lambda:[source]),patch.object(builder,'reviewed_labels',lambda:{}),patch.object(builder,'translate_small',translate),patch.object(builder.time,'sleep',lambda _:None),patch('sys.argv',['builder','--stage',str(stage)]),contextlib.redirect_stdout(io.StringIO()):code=builder.main()
   return code,json.loads((stage/'progress.json').read_text())
 def test_provider_failure_is_nonzero_and_preserved(self):
  code,progress=self.run_build(True);self.assertEqual(code,1);self.assertEqual(progress['failures'][0]['language'],'fr');self.assertFalse(progress['finalApproval'])
 def test_completed_requested_build_succeeds_without_approval(self):
  code,progress=self.run_build(False);self.assertEqual(code,0);self.assertEqual(progress['completed'],['fr']);self.assertFalse(progress['finalApproval'])
if __name__=='__main__':unittest.main()
