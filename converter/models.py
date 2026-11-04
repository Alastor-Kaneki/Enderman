"""Offline Java Edition block model resolver for resource-pack ZIPs."""
import json
import zipfile

class ModelError(ValueError):
    pass

def identifier(value, default_namespace="minecraft"):
    return value.split(":", 1) if ":" in value else (default_namespace, value)

class ModelResolver:
    def __init__(self, archive):
        self.archive = archive
        self.cache = {}
    def _read(self, name):
        namespace, path = identifier(name)
        filename = f"assets/{namespace}/models/{path}.json"
        try:
            with zipfile.ZipFile(self.archive) as z:
                return json.loads(z.read(filename))
        except KeyError as exc:
            raise ModelError(f"Missing model: {filename}") from exc
    def resolve(self, name, stack=()):
        if name in self.cache:
            return self.cache[name]
        if name in stack:
            raise ModelError("Cyclic model inheritance: " + " -> ".join((*stack, name)))
        data = self._read(name)
        parent = data.get("parent")
        base = self.resolve(parent, (*stack, name)) if parent else {}
        result = dict(base)
        # Child elements replace parent elements; other inherited keys merge.
        for key, value in data.items():
            if key == "textures":
                result[key] = {**base.get(key, {}), **value}
            elif key == "display":
                result[key] = {**base.get(key, {}), **value}
            else:
                result[key] = value
        result.pop("parent", None)
        self.cache[name] = result
        return result
    def texture(self, model, ref):
        textures = model.get("textures", {})
        seen = set()
        while ref.startswith("#"):
            key = ref[1:]
            if key in seen:
                raise ModelError("Cyclic texture reference: " + key)
            seen.add(key)
            if key not in textures:
                raise ModelError("Missing texture variable: " + key)
            ref = textures[key]
        return ref
    def geometry(self, name):
        model = self.resolve(name)
        elements = []
        for element in model.get("elements", []):
            faces = {}
            for direction, face in element.get("faces", {}).items():
                face = dict(face)
                if "texture" in face:
                    face["texture"] = self.texture(model, face["texture"])
                faces[direction] = face
            elements.append({**element, "faces": faces})
        return {"model": name, "ambientocclusion": model.get("ambientocclusion", True), "elements": elements}
