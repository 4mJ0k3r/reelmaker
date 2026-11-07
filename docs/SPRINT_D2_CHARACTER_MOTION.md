# Scout and Mechanic contact refinement

The opt-in refined pose uses a fixed horizontal footprint through each stance.
The interaction blend scales swing height and gesture amplitude. It no longer
slides the planted footprint toward the moving pelvis at gait ramp boundaries.
Existing 0.1 requests preserve their original motion. Scout has a quicker
reaction and a freer arm swing, while Mechanic settles over a longer interval.

`tools/sprint_d_contacts.py` samples the same registered rigs at 30 fps before
and after the change. It measures consecutive ankle samples at ground height
and reports the maximum drift in world units at the authored .78 staging scale.
Pickup and push drift drop from 1.58–1.86 units to under 2.3e-14. The maximum
hand socket error remains under 2.3e-14. Walk, run and the five transitions per
actor have separate sample rows in the review evidence.
