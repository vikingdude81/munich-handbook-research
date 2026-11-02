# Numogram ground-truth report 2026-11-02

distilled files: distilled_000.json, distilled_001.json
entities: 26  relationships: 9  passages: 10

## Checks
- gold endpoint-rule self-test: 1890~1::0, 271890~2::0, 27541890~2::0, 1872~2::1, 271~2::1, 27541~2::1, 18723~3::1, 1872563~3::1
- rite recall: 8/8
- rite fabrication: 0 non-corpus strings in rite context
- demons with correct pole: 4/4 -> ['Lurgo (pole present, unbound format)', 'Duoddod (pole present, unbound format)', 'Doogu (pole present, unbound format)', 'Ixigool (pole present, unbound format)']
- endpoint-pole invariant on extracted pairs: 12 checked, 0 bound to wrong demon (cross-binding errors: [])
- apparatus terms: 12/12 (missing [])
- definition fidelity: 5/8 (missing ['currents', 'demon_nature', 'necronomicon_link'])
- time-systems: 3/3
- provenance signal terms: ['ccru', 'lemurian', 'fiction']

## Fails
## Warns

**VERDICT: PASS**  (rite recall 1.00, fabrications 0)