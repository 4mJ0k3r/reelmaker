# Abandoned Outpost and Forest Ravine

Abandoned Outpost frames a damaged roadside route below a watch shelter and a
distant communications mast. Forest Ravine uses a diagonal channel, a winding
upper-bank footpath, fir silhouettes and a split distant peak. Each location
registers three fixed moods. Both use the existing bounded scene graph.

| World | Moods | Staging |
| --- | --- | --- |
| Abandoned Outpost | daylight, sunset, storm | Road apron in front of the shelter |
| Forest Ravine | morning, misty, night | Upper path, with the channel behind the actors |

The logical view is 360 × 640. Sky fills the image behind all layers. Terrain
extends from −510 to 880 horizontally and through y=1103, beyond supported
camera crops. The registered actor support rectangle is x=−180…540,
y=535…790. Both worlds put the acting floor at y=581 and use parallax depth 1
for ground and actors. The near rock, scrub and bough silhouettes sit on a
foreground layer at depth 1.4. Existing pine, lamp, fence and weather assets
supply the remaining detail. The five new records cover the two panoramas,
two supporting ground pieces and the outpost shelter.

The six world examples under `examples/living-worlds` are editable scene
manifests. Production selection uses the additive cinematic project contract.
