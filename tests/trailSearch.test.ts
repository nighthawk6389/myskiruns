// Run with `npm test`. The search over every resort's trails (src/trailSearch.ts).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { searchTrails, type TrailIndex } from '../src/trailSearch.ts';

const index: TrailIndex = {
  resorts: [
    ['killington', 'Killington', 'Vermont'],
    ['vail', 'Vail', 'Colorado'],
    ['jay-peak', 'Jay Peak', 'Vermont'],
  ],
  trails: [
    [0, 'outer-limits', 'Outer Limits', 'double-black'],
    [0, 'lower-great-northern', 'Lower Great Northern', 'green'],
    [1, 'riva-ridge', 'Riva Ridge', 'black'],
    [1, 'lower-riva', 'Lower Riva', 'blue'],
    [2, 'the-jet', 'The Jet', 'black'],
    [2, 'ullrs-dream', "Ullr's Dream", 'blue'],
    [1, 'outer-limits-vail', 'Outer Limits', 'black'],
  ],
};
const names = (q: string) => searchTrails(index, q).hits.map((h) => `${h.name} @ ${h.resortName}`);

test('the same name at two resorts: both, by resort', () => {
  assert.deepEqual(names('outer limits'), ['Outer Limits @ Killington', 'Outer Limits @ Vail']);
});

test('names that start with the query come before a word inside a name', () => {
  assert.deepEqual(names('riva'), ['Riva Ridge @ Vail', 'Lower Riva @ Vail']);
});

test('words in any order, case and apostrophes ignored', () => {
  assert.deepEqual(names('northern lower'), ['Lower Great Northern @ Killington']);
  assert.deepEqual(names('ULLRS'), ["Ullr's Dream @ Jay Peak"]);
  assert.deepEqual(names('ullr’s dr'), ["Ullr's Dream @ Jay Peak"]);
});

test('a hit carries its resort and rating; short queries find nothing; a limit keeps the total', () => {
  const [hit] = searchTrails(index, 'jet').hits;
  assert.deepEqual(hit, { resortId: 'jay-peak', resortName: 'Jay Peak', region: 'Vermont', trailId: 'the-jet', name: 'The Jet', difficulty: 'black' });
  assert.equal(searchTrails(index, 'o').total, 0);
  const r = searchTrails(index, 'outer', 1);
  assert.equal(r.hits.length, 1);
  assert.equal(r.total, 2);
});
