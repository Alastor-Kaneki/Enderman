# ModelBridge offline Java model tools

Run `python3 -m unittest discover -p 'test_*.py' -v` from this directory.

`blockstates.py` selects Java blockstate variant/multipart model references.
`models.py` resolves model parent chains, inherited textures, texture aliases and model elements.

These tools do **not** render models in Bedrock. Rotation, tint, face culling, geometry conversion, texture atlas building, vanilla block mapping, and native renderer interception remain future work.
