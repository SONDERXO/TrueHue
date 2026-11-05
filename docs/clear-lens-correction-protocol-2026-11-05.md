# Clear prescription lenses: fixed saved-output comparison

5November2026. User requests correcting through see-through prescription lenses,
including the visible eye region, while excluding only frames/rims. Sunglasses
remain opaque objects. This is a correction-region change, not measurement
admission through lenses or a new automatic glasses-type classifier.

Use all same12 saved FFHQ cases, no new inference or variants. Explicitly mark
16061 and59807 as clear-lens examples from the already inspected originals;
29617 is sunglasses. Other cases use unchanged opaque/unknown policy. These
are assistant visual designations for this bounded comparison, not verified
prescriptions, optical properties, training labels or automatic detection.

The parser has only one glasses class, covering lenses and frames together.
Use one fixed engineering approximation: fill enclosed holes in class6 to
obtain its envelope; retain a two-pixel inner boundary band on the existing
256px frame as approximate rims/bridge/arms. Narrow bridges remain protected.
Restore the remaining interior only within original face/correction support
and facial skin/feature/glasses labels1/2/3/4/5/6/10. Explicit caller protection
and other object classes always win. Override both class6 and FaceOcc's glasses
veto inside those declared clear interiors. Do not use eye/brow measurement
holes as correction exclusions. Missing interiors remain unavailable.

This is approximate geometry, NOT frame segmentation truth. It can protect
some visible skin or miss wires/reflections inside lenses. No image-threshold,
width sweep, new model or manual frame tracing. Record the limitation plainly.

Build a new package, preserve all earlier outputs/modules and freeze dependencies
before processing. Check all12, retain failures; inspect both clear examples
and the unchanged sunglasses example. Save masks/rim/lens overrides, old/new
overlays, exact alpha and illustrative .85/1.05/.95 rendering. Verify support
subset of original, restoration confined to lenses, unchanged other cases and
measurement, zero rim/protected alpha/byte changes, and exact neutral identity.
Independent alpha/RGB8 checks and focused tests cover clear vs opaque lenses,
visible eye correction, bridge/rim protection and explicit protection precedence.
No MST/tree/target fitting, admissions, publication, contacts or runtime switch.
