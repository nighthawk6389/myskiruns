export const meta = {
  name: 'trailmap-readers',
  description: 'Parallel readers name every numbered line piece of a trail map and record every printed label (prompts/0-new-map.md)',
  whenToUse: 'Recipe E of docs/trail-map-playbook.md (Part 4: the readers), after render_tiles.py. Pass args like tools/trailmap/runs/stowe-readers.json.',
  phases: [{ title: 'Read', detail: 'one reader per group of neighbouring tiles' }],
}

// args: {resort, tilesDir, sourceImage, zoom, legend, areas, groups: [[tile ids]]}
// Each reader follows tools/trailmap/prompts/0-new-map.md itself, so the
// prompt file stays the single source of the instructions.
phase('Read')
const results = await parallel(args.groups.map((g, i) => () => {
  const values = {
    RESORT: args.resort,
    TILE_PATHS: g.map((t) => `${args.tilesDir}/${t}.jpg`).join(', '),
    ZOOM: String(args.zoom ?? 1.7),
    TILES_DIR: args.tilesDir,
    SOURCE_IMAGE: args.sourceImage,
    LEGEND: args.legend,
    AREAS: args.areas,
    OUT_FILE: `${args.tilesDir}/result_${i}.json`,
  }
  const prompt = [
    'Read tools/trailmap/prompts/0-new-map.md in the repository. Carry out the',
    'instructions after its "---" line exactly, substituting these values for',
    'the {{PLACEHOLDERS}}:',
    ...Object.entries(values).map(([k, v]) => `{{${k}}} = ${v}`),
  ].join('\n')
  return agent(prompt, { label: `reader ${i}: ${g.join(' ')}`, phase: 'Read' })
}))
return results.map((r, i) => ({ group: args.groups[i], summary: r }))
