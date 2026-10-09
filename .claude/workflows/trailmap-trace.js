export const meta = {
  name: 'trailmap-trace',
  description: 'Parallel readers trace trails with no drawn line, traverses and uncertain proposals (prompts/4-trace.md)',
  whenToUse: 'Recipes E and F of docs/trail-map-playbook.md (Part 4: the trace pass), before the human review. Pass args like tools/trailmap/runs/stowe-trace.json.',
  phases: [{ title: 'Trace', detail: 'one reader per ~5 trails' }],
}

// args: {resort, sourceImage, width, height, tilesDir, zoom, polylines,
//        legend, outDir, groups: ["id x | NAME | difficulty | label [[x,y]] | what we know\n..."]}
phase('Trace')
const results = await parallel(args.groups.map((g, i) => () => {
  const values = {
    RESORT: args.resort,
    SOURCE_IMAGE: args.sourceImage,
    W: String(args.width),
    H: String(args.height),
    TILES_DIR: args.tilesDir,
    ZOOM: String(args.zoom ?? 1.7),
    POLYLINES: args.polylines,
    LEGEND: args.legend,
    TRAILS: '\n' + g + '\n',
    OUT_FILE: `${args.outDir}/trace_${i}.json`,
  }
  const prompt = [
    'Read tools/trailmap/prompts/4-trace.md in the repository. Carry out the',
    'instructions after its "---" line exactly, substituting these values for',
    'the {{PLACEHOLDERS}}:',
    ...Object.entries(values).map(([k, v]) => `{{${k}}} = ${v}`),
  ].join('\n')
  return agent(prompt, { label: `tracer ${i}`, phase: 'Trace' })
}))
return results
