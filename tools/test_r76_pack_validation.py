"""Regression checks for legitimate identical labels and strict leak detection."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location("builder",Path(__file__).with_name("r35_build_pack.py"))
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class PackValidation(unittest.TestCase):
    def build_pack(self,code,values):
        source=["Contact","Privacy","Terms"]
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(b,"OUT",Path(folder)), patch.object(b,"languages",return_value=[code]), patch.object(b,"source_meta",return_value=(source,"test-hash")), patch.object(b,"google_translate",return_value=values), patch.object(b,"repair_unchanged",side_effect=lambda c,s,v:v):
                b.build(code)
                return json.loads((Path(folder)/(code+".json")).read_text())
    def test_cognates_write_complete_packs(self):
        for code,values in [("fr",["Contact","Confidentialité","Conditions"]),("it",["Contatti","Privacy","Termini"]),("nl",["Contact opnemen","Privacy","Voorwaarden"])]:
            with self.subTest(code=code):
                data=self.build_pack(code,values)
                self.assertEqual(data["count"],3)
                self.assertEqual(data["sourceHash"],"test-hash")
                self.assertEqual(list(data["translations"].values()),values)
    def test_untranslated_forced_labels_still_fail(self):
        for code,values in [("fr",["Contact","Privacy","Conditions"]),("de",["Contact","Datenschutz","Bedingungen"])]:
            with self.subTest(code=code), self.assertRaisesRegex(RuntimeError,"forced UI remained English"):
                self.build_pack(code,values)
    def test_corrupt_output_still_fails(self):
        with self.assertRaisesRegex(RuntimeError,"corrupt oversized"):
            self.build_pack("fr",["Contact","x"*1000,"Conditions"])

if __name__=="__main__":unittest.main()
