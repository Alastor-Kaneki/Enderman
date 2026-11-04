import json
import tempfile
import unittest
import zipfile
from blockstates import resolve

class BlockstatesTest(unittest.TestCase):
    def test_variants_and_multipart(self):
        with tempfile.NamedTemporaryFile(suffix=".zip") as f:
            with zipfile.ZipFile(f.name, "w") as z:
                z.writestr("assets/minecraft/blockstates/test.json", json.dumps({"variants":{"facing=north":{"model":"north"},"facing=south":{"model":"south"}}}))
                z.writestr("assets/minecraft/blockstates/multi.json", json.dumps({"multipart":[{"apply":{"model":"base"}},{"when":{"OR":[{"north":"true"},{"south":"true"}]},"apply":{"model":"side"}}]}))
            self.assertEqual(resolve(f.name, "test", {"facing":"north"})[0]["model"], "north")
            self.assertEqual(len(resolve(f.name, "multi", {"north":"true"})), 2)
            self.assertEqual(len(resolve(f.name, "multi", {"north":"false"})), 1)

if __name__ == "__main__":
    unittest.main()
