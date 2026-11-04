import json
import tempfile
import unittest
import zipfile
from models import ModelResolver, ModelError

class ModelsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix=".zip")
        with zipfile.ZipFile(self.temp.name, "w") as z:
            def add(name, value):
                z.writestr("assets/minecraft/models/" + name + ".json", json.dumps(value))
            add("block/base", {"textures":{"all":"minecraft:block/stone","side":"#all"},"elements":[{"from":[0,0,0],"to":[16,16,16],"faces":{"north":{"texture":"#side"}}}]})
            add("block/child", {"parent":"minecraft:block/base","textures":{"all":"minecraft:block/glass"}})
            add("block/cycle1", {"parent":"minecraft:block/cycle2"})
            add("block/cycle2", {"parent":"minecraft:block/cycle1"})
            add("block/override", {"parent":"minecraft:block/base","elements":[]})
        self.resolver = ModelResolver(self.temp.name)
    def tearDown(self):
        self.temp.close()
    def test_inherited_texture(self):
        geometry = self.resolver.geometry("minecraft:block/child")
        self.assertEqual(geometry["elements"][0]["faces"]["north"]["texture"], "minecraft:block/glass")
    def test_child_elements_override(self):
        self.assertEqual(self.resolver.geometry("block/override")["elements"], [])
    def test_parent_cycle(self):
        with self.assertRaises(ModelError):
            self.resolver.resolve("block/cycle1")
    def test_missing(self):
        with self.assertRaises(ModelError):
            self.resolver.resolve("block/unknown")
if __name__ == "__main__":
    unittest.main()
