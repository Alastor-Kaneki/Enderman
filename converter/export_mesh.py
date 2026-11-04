"""CLI: python3 export_mesh.py resource-pack.zip minecraft:block/end_rod output.json"""
import json
import sys
from mesh import convert_archive

def main():
    if len(sys.argv)!=4:
        raise SystemExit("Usage: export_mesh.py PACK.zip MODEL_ID OUT.json")
    result=convert_archive(sys.argv[1],sys.argv[2])
    with open(sys.argv[3],"w",encoding="utf-8") as f:
        json.dump(result,f,indent=2)
    print(f"Exported {len(result['quads'])} quads to {sys.argv[3]}")

if __name__=="__main__":
    main()
