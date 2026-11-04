import json
import tempfile
import unittest
import zipfile
from mesh import convert_archive

class MeshTest(unittest.TestCase):
    def test_quads_uv_and_cull(self):
        with tempfile.NamedTemporaryFile(suffix=".zip") as f:
            model = {"textures":{"all":"minecraft:block/stone"},
                     "elements":[{"from":[0,0,0],"to":[16,16,16],
                                  "faces":{"north":{"texture":"#all","cullface":"north"},
                                           "up":{"texture":"#all"}}}]}
            with zipfile.ZipFile(f.name,"w") as z:
                z.writestr("assets/minecraft/models/block/sample.json",json.dumps(model))
            result=convert_archive(f.name,"minecraft:block/sample")
            self.assertEqual(len(result["quads"]),2)
            self.assertEqual(result["quads"][0]["texture"],"minecraft:block/stone")
            self.assertEqual(result["quads"][0]["cullface"],"north")
            self.assertEqual(len(result["quads"][0]["vertices"]),4)
            self.assertEqual(result["quads"][1]["uv"],[0,0,16,16])

if __name__=="__main__":
    unittest.main()
