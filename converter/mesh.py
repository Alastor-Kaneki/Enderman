"""Convert resolved Java block model elements into a renderer-neutral mesh.
Coordinates remain in Java's 0..16 block coordinate system.
This is an intermediate format, NOT a Bedrock geometry definition.
"""
from models import ModelResolver

DIRECTIONS = {
    "down": lambda a,b: [(a[0],a[1],a[2]),(b[0],a[1],a[2]),(b[0],a[1],b[2]),(a[0],a[1],b[2])],
    "up": lambda a,b: [(a[0],b[1],b[2]),(b[0],b[1],b[2]),(b[0],b[1],a[2]),(a[0],b[1],a[2])],
    "north": lambda a,b: [(b[0],a[1],a[2]),(a[0],a[1],a[2]),(a[0],b[1],a[2]),(b[0],b[1],a[2])],
    "south": lambda a,b: [(a[0],a[1],b[2]),(b[0],a[1],b[2]),(b[0],b[1],b[2]),(a[0],b[1],b[2])],
    "west": lambda a,b: [(a[0],a[1],a[2]),(a[0],a[1],b[2]),(a[0],b[1],b[2]),(a[0],b[1],a[2])],
    "east": lambda a,b: [(b[0],a[1],b[2]),(b[0],a[1],a[2]),(b[0],b[1],a[2]),(b[0],b[1],b[2])],
}

def build_mesh(resolver, model_name):
    source = resolver.geometry(model_name)
    quads = []
    for element in source["elements"]:
        a, b = element["from"], element["to"]
        if len(a) != 3 or len(b) != 3 or any(float(a[i]) > float(b[i]) for i in range(3)):
            raise ValueError("Invalid model element bounds")
        rotation = element.get("rotation")
        for direction, face in element.get("faces", {}).items():
            if direction not in DIRECTIONS:
                raise ValueError(f"Unknown face direction: {direction}")
            uv = face.get("uv")
            if uv is None:
                # Default Java UVs depend on the face direction.
                x1,y1,z1 = a
                x2,y2,z2 = b
                uv = {
                    "down":[x1,16-z2,x2,16-z1],
                    "up":[x1,z1,x2,z2],
                    "north":[16-x2,16-y2,16-x1,16-y1],
                    "south":[x1,16-y2,x2,16-y1],
                    "west":[z1,16-y2,z2,16-y1],
                    "east":[16-z2,16-y2,16-z1,16-y1],
                }[direction]
            quads.append({
                "vertices": DIRECTIONS[direction](a,b),
                "texture": face.get("texture"),
                "uv": uv,
                "uv_rotation": face.get("rotation", 0),
                "cullface": face.get("cullface"),
                "tintindex": face.get("tintindex"),
                "element_rotation": rotation,
                "shade": element.get("shade", True),
            })
    return {"format":"modelbridge.quads.v1", "model":model_name,
            "ambientocclusion":source["ambientocclusion"], "quads":quads}

def convert_archive(archive, model_name):
    return build_mesh(ModelResolver(archive), model_name)
