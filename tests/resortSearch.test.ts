// Run with `npm test`. The resort picker's search (src/resortSearch.ts).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { byRegion, fold, searchResorts } from '../src/resortSearch.ts';

const resorts = [
  { id: 'killington', name: 'Killington', region: 'Vermont' },
  { id: 'stowe', name: 'Stowe', region: 'Vermont' },
  { id: 'jay-peak', name: 'Jay Peak', region: 'Vermont' },
  { id: 'smugglers-notch', name: "Smugglers' Notch", region: 'Vermont' },
  { id: 'copper-mountain', name: 'Copper Mountain', region: 'Colorado' },
  { id: 'hunter', name: 'Hunter Mountain', region: 'New York' },
  { id: 'wildcat', name: 'Wildcat Mountain', region: 'New Hampshire' },
  { id: 'vail', name: 'Vail', region: 'Colorado' },
  { id: 'sunday-river', name: 'Sunday River', region: 'Maine' },
];
const ids = (q: string) => searchResorts(resorts, q).map((r) => r.id);

test('an empty query lists every resort by name', () => {
  assert.deepEqual(ids(''), [
    'copper-mountain',
    'hunter',
    'jay-peak',
    'killington',
    'smugglers-notch',
    'stowe',
    'sunday-river',
    'vail',
    'wildcat',
  ]);
  assert.deepEqual(ids('   '), ids(''));
});

test('a name prefix comes before a word prefix, a word prefix before a substring', () => {
  assert.deepEqual(ids('s'), ['smugglers-notch', 'stowe', 'sunday-river']);
  // "mountain" starts a word of three names; nothing starts with it
  assert.deepEqual(ids('mountain'), ['copper-mountain', 'hunter', 'wildcat']);
  // "ton" is inside Killington only
  assert.deepEqual(ids('ton'), ['killington']);
  assert.deepEqual(ids('mountain c'), []);
});

test('case, accents, apostrophes, hyphens and spaces are ignored', () => {
  assert.deepEqual(ids('KILL'), ['killington']);
  assert.deepEqual(ids('smugglers notch'), ['smugglers-notch']);
  assert.deepEqual(ids('Smugglers’ Notch'), ['smugglers-notch']);
  assert.deepEqual(ids('jaypeak'), ['jay-peak']);
  assert.deepEqual(ids('jay-peak'), ['jay-peak']);
  assert.equal(fold('Côte  '), 'cote');
});

test('a state, or its postal abbreviation, finds its resorts after any name match', () => {
  assert.deepEqual(ids('colorado'), ['copper-mountain', 'vail']);
  assert.deepEqual(ids('vt'), ['jay-peak', 'killington', 'smugglers-notch', 'stowe']);
  assert.deepEqual(ids('new'), ['hunter', 'wildcat']);
  // "co" starts "Copper" (a name match) before Colorado's other resort
  assert.deepEqual(ids('co'), ['copper-mountain', 'vail']);
  assert.deepEqual(ids('me'), ['sunday-river']);
});

test('a resort is also found by the other places it lists, and grouped by its region alone', () => {
  const tahoe = [
    { id: 'palisades-tahoe', name: 'Palisades Tahoe', region: 'California', also: ['Lake Tahoe'] },
    { id: 'heavenly', name: 'Heavenly', region: 'California', also: ['Nevada', 'Lake Tahoe'] },
  ];
  const find = (q: string) => searchResorts(tahoe, q).map((r) => r.id);
  assert.deepEqual(find('nevada'), ['heavenly']);
  assert.deepEqual(find('nv'), ['heavenly']);
  // a name match before a place match
  assert.deepEqual(find('tahoe'), ['palisades-tahoe', 'heavenly']);
  assert.deepEqual(find('lake tahoe'), ['heavenly', 'palisades-tahoe']);
  assert.deepEqual(find('ca'), ['heavenly', 'palisades-tahoe']);
  assert.deepEqual(byRegion(tahoe).map((g) => [g.region, g.resorts.map((r) => r.id)]), [
    ['California', ['heavenly', 'palisades-tahoe']],
  ]);
});

test('nothing matches a word no resort has', () => {
  assert.deepEqual(ids('whistler'), []);
});

test('grouped by state, states and resorts in alphabetical order', () => {
  assert.deepEqual(
    byRegion(resorts).map((g) => [g.region, g.resorts.map((r) => r.id)]),
    [
      ['Colorado', ['copper-mountain', 'vail']],
      ['Maine', ['sunday-river']],
      ['New Hampshire', ['wildcat']],
      ['New York', ['hunter']],
      ['Vermont', ['jay-peak', 'killington', 'smugglers-notch', 'stowe']],
    ],
  );
});
