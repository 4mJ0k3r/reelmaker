# ReelMaker visual style guide

**Direction · Cut planes, soft air.** Build scenes from broad, sculpted shapes, with
crisper silhouettes around the story action and softer edges as the world recedes.
Use directional light to describe mass, weather and time of day. A frame should
read first as a place, then as a character doing something specific. The same
rules apply to a village at dusk, a historical setting and a cold suspense scene.
Originality comes from the scene's own silhouettes, materials and staging.

[Palette and shape board](visual-evidence/stage0c/palette.svg) ·
[Existing-engine stills](visual-evidence/stage0c/README.md) ·
[Review rubric](VISUAL_QUALITY_RUBRIC.md)

## Shape and edge language

| Level | Implementation rule |
| --- | --- |
| Primary | Start with one recognizable outer contour and one dominant direction. Give organic forms a broad mass and a smaller offset mass. Use the primary shape to establish species, posture, function or load-bearing structure. |
| Secondary | Add two or three large planes to show overlap, weight and the direction of light. Change taper, angle or silhouette across variants. For a tree, vary branch departure and crown balance before adding leaves. |
| Tertiary | Group small cuts, cracks or seams in a few places, especially near a contact point or lit edge. Preserve blank surfaces. Omit marks that disappear or shimmer at reduced display size. |

Organic contours should alternate tapered curves, short flats and deliberate gaps.
Architecture can use straight lines and repeated bays, with breaks at corners,
recesses and material joins. Maintain shared perspective for repeated bays.
Primitive shapes work as construction guides. Break a uniform circle with a
change of curvature, a taper, or an overlapping mass. Break a featureless
rectangle with a return plane, reveal, cap or inset that explains how it is built.
Reserve regular geometry for objects whose function calls for it.

Use filled silhouettes as the default. Add local outlines where two similar
values touch. As an initial target at 720 px output width, use 2–4 px for a
nearby structural edge, 1–2 px for supporting edges and value boundaries alone
for distant shapes. Keep a curve's highlight on the lit shoulder and its darkest
edge near contact or occlusion. At 360 × 640, check that the silhouette survives
before evaluating surface detail. Add texture only when it helps establish
material, scale or focus.

## Color system

Values are sRGB hex design targets for future artwork. Key and fill are color
references for mixing planes and gradients. Their final opacity depends on
material and distance. Keep foreground and midground value groups distinct.

| Mood | Sky high | Air/horizon | Ground base | Key | Fill | Deep contact | Accent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Warm daylight | #5E8290 | #CBD0AD | #58644C | #E4C995 | #78909A | #24343A | #C96849 |
| Golden dusk | #505D7A | #DBA883 | #526052 | #F4C184 | #727B92 | #2A313E | #E68156 |
| Cold suspense | #293B59 | #8FA8B6 | #798F9D | #D4DFE0 | #627D9D | #202B40 | #EDA65F |
| Storm danger | #343D51 | #75838D | #505F65 | #BDC6B9 | #627686 | #242C3A | #E47758 |

Shared material anchors are lichen green `#626F52`, earth ochre `#8E6F53`,
stone slate `#65747C`, aged wood `#806150`, snow pearl `#DCE5E4`,
metal blue-grey `#7C8B94`, and glass air-blue `#9BB7BB`. Grade each toward
the mood's key on lit planes and its fill on turning planes. Reserve the strongest
local color contrast for one face, gesture or story object. Choose either an
accent on the character or an accent in the environment as the primary color
cue. Let background chroma and fine contrast fall with distance by mixing
toward the air color. In cold scenes, keep the warm accent local. In warm
scenes, cool fill keeps forms from merging into the horizon.

| Material | Vector treatment |
| --- | --- |
| Earth | Broad warm/cool planes, shallow edge cuts at exposed soil and sparse clustered grit near contact. A gentle ground gradient can describe distance. |
| Vegetation | Two or three overlapping canopy masses, asymmetric taper and small lit cuts on the outer edge. Keep interior leaf marks clustered. |
| Rock | Large planar facets, one clear fracture direction and an occluded base. Allow curved erosion on the silhouette, with crisp fractures nearer the camera. |
| Wood | Value changes at joints, tapered grain groups along the construction axis and dark gaps at actual seams. |
| Snow | Pearl body, blue fill on turned planes, broad drifts and sharp rock/snow overlaps. Leave wide clean areas. Darken under compression or occlusion. |
| Metal | Tight directional highlight and a controlled dark reflection. Keep sharp accents small and respond consistently to the key. |
| Cloth | Large folds pulled from seams and joints, softer turning edges, a restrained highlight and clear hems. |
| Glass | Tinted plane with one or two reflected shapes and a thin high-value edge. Align highlights with the dominant light and keep the subject behind readable. |

Favor solid planes first. Add a simple linear gradient to show air, a broad
turning surface or a local falloff. Use a few translucent vector shapes for
soft edges. Avoid layered full-frame transparency or dense texture fields
until the cost has been measured.

## Space, scale and depth

**Current engine.** Existing scenes use a 360 × 640 logical canvas for
720 × 1280 delivery, with screen x right and y down. Placement, painter order
and layer depth are explicit. Perspective is authored in geometry and
staging. Layers share their projection and support-aware character placement
uses a declared ground envelope. That envelope is an admission bound.
It does not resolve slopes, collision or foot placement on a mesh. Storyboard
framing applies its own camera behavior. Current controls and caps are in
[Scene graph](SCENE_GRAPH.md) and [Cinematic direction](CINEMATIC_DIRECTION.md).

**Art standard.** Establish a horizon and a dominant ground direction in each
set. Start a wide shot with the horizon around 35–55% of the frame height,
then adjust to emphasize sky, scale or terrain. Place the character's sole
and the object's base on the same authored ground at their respective depths.
Keep same-plane foot and shadow anchors together through camera moves. At
matched depth, start with a doorway around 1.15–1.35 times the intended
human figure's height, then adjust for the world and architecture. Use the
actual standing height declared by each rig to compare figures. Derive tree
and rock size from species, use and setting. Check door, human, road edge,
rock and trunk in one overlay before removing the construction guides.

Stack distant sky and landforms, a playable midground and an optional near
occluder. Separate them with overlap, progressively narrower value ranges
toward the distance and lower detail in the far layer. Scale objects along
the road's recession, align façade returns to its chosen perspective and
let ground surfaces continue behind actors. Use parallax as a restrained
depth cue: the foreground moves more on a pan and the far silhouette moves
less. Maintain the planned painter order as well as the assigned depth.
Check the start, end and any crossing in a move for tangencies, depth slips
and sky gaps. Hand-author any crossing that needs a new occlusion order.

## Lighting and atmosphere

1. **Key.** Pick a side and elevation in the shot brief. Face broad light
   planes toward the source. Draw cast shapes away from it. Keep direction
   consistent across the character, foliage, props and successive cuts.
2. **Fill.** Mix the turning planes toward the environment fill. In
   overcast scenes compress the lit-to-shadow interval. At night preserve
   facial and hand readability with a separated background value or broad
   cool fill.
3. **Contact.** Seat feet, tires, trunks and rocks with a compact dark shape
   at the anchor, then extend a softer lower-opacity shape along the
   ground. An airborne character keeps a weaker, displaced ground cue
   where the shot needs it. Check planted poses at the contact frame.
4. **Rim and local light.** Reserve a narrow rim for backlit contours
   facing the light. A practical source needs a visible emitter, falloff
   and selective nearby response. Anchor a beacon's glow to the housing
   and illuminate the face or snow only where the authored geometry and
   staging support it.
5. **Air and weather.** Increase the air-color mix behind the playable
   plane. Keep haze and weather marks sparse around eyes, hands and the
   story prop. Give moving particles a consistent wind direction and
   deterministic time behavior. Keep storm accents brief enough to
   preserve the action.

These are authoring rules for Cairo fills, gradients, clips and layered shapes.
Existing recipes already grade some materials and implement local effects.
Shared light transport, dynamic shadow casting and a global weather simulator
are future capabilities.

## Characters

Yellow Mellow V2 retains his black round head, large white eyes, red pom
beanie, yellow hoodie and dark limbs/shorts. Use his face and cap contour as
primary identifiers. Keep the head round while changing the eye apertures,
pupil placement, pose and garment folds. Rowan retains his existing silhouette,
costume, facial treatment and declared proportions. Verify any appearance
change against a reference pose from the existing rig.

Design new figures with distinguishable head-to-body ratio, torso taper,
stance, costume construction and movement rhythm. A future reusable humanoid
rig should separate joints and ground/contact conventions from the individual
silhouette, garment topology, expression design and timing. Validate each
body type on its own contact poses. Avoid treating a palette swap as a new
identity.

Keep an eye line and a clear leading gesture. Change weight and tilt with
emotion. At a glance, the pose should convey intent before small face details
are visible. Group fingers for wide shots and separate the thumb and
contacting finger when a close action depends on them. Draw shoes with a
recognizable toe and planted sole. Define hoodie seams, cuffs and hems by how
the garment hangs around joints. Check neutral, extremes and transitions for
scale drift, merged limbs, floating soles and broken clothing. Use the same
world key and fill as the set while preserving identifying colors.

## Vertical framing and cuts

Work at **720 × 1280, 9:16, 30 FPS**. Check at full resolution and at
360 × 640. As a staging aid, keep essential detail away from the outer
10% on the sides, top 10% and bottom 18%. Check the intended delivery UI
overlay separately. Keep a quiet value area behind the action and leave
look or travel room in its direction.

| Shot | Staging rule |
| --- | --- |
| Establishing | Show a near cue, a navigable midground and a distant shape. Keep the actor or route readable against a single large value mass. |
| Medium | Keep the face and active hand visible at once. Let the cropped surroundings explain the space. Avoid cutting directly at hands or joints during the key gesture. |
| Close-up | Give eyes, expression or contact the highest edge contrast. Place empty space in the gaze direction. Remove crossing edges from behind the face. |
| Object reveal | Establish the object position with an eyeline or occlusion edge, reveal its silhouette and hold through the moment its purpose reads. |
| Suspense | Use negative space for the expected threat and a partial foreground shape to frame the wait. Hold the primary action legible as weather or lighting changes. |

Start with a locked or gently moving frame. Give a push or follow one clear
purpose. Check the entire move for planted-foot drift and foreground tangencies.
Across cuts, preserve the screen direction of travel and gaze, the relative
position of the object, and the dominant light direction. Use a deliberate
reframe when changing axes. Judge continuity and timing on consecutive
frames before a future asset is approved.

## Family standards

| Family | Minimum review requirements |
| --- | --- |
| Nature | For sky and terrain, keep horizon and scale coherent. Tree variants change silhouette and branch rhythm, use a known trunk anchor and reserve wind motion for supported implementations. Ground declares its playable extent. Rock variants retain credible contact and scale. |
| Architecture | Identify a base anchor, façade plane, return plane and door reference. Keep openings, stairs and seams coherent with structure and actor scale. Treat interiors as separately authored where supported. |
| Props | Record function, scale, stable orientation and placement anchor. Preserve the recognizable profile across variants. Document a contact socket only when the implementation and preview establish one. |
| Effects | Identify the source, direction, duration, draw order and maximum density. Keep the unoccluded gesture readable and supply a representative peak-intensity frame. |
| Lighting | Declare key and fill roles, contact treatment, local-light falloff and layer ownership. Supply a bright and a low-key read of the same subject. |
| Materials | Record palette roles, representative surfaces and which details survive at 360 × 640. Use repeatable sampling and a declared geometry/transparency budget. |
| Composition | Document horizon, depth assignments, focal target, support plane and camera limits. Check occlusion, mobile framing and continuity through the relevant motion. |

For every family, use the existing runtime interface and submit the evidence in
the [quality rubric](VISUAL_QUALITY_RUBRIC.md).
