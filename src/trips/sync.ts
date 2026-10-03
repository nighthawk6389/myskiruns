// One sync of this device's trips with the account's copy (pure: the copy is
// passed in, so tests can stand in for Supabase). Read the saved copy, merge,
// and save the result only if the copy hasn't changed since it was read (its
// version): two devices saving at once can't overwrite each other, the slower
// one reads again and merges again.
// (.ts extension: the tests run this file in Node, which needs it)
import { mergeTrips, sameTrips, type Trip } from './log.ts';

export interface SavedTrips {
  read(): Promise<{ trips: Trip[]; version: number } | null>;
  /** false if a copy was created meanwhile */
  create(trips: Trip[]): Promise<boolean>;
  /** false if the copy is no longer at `version` */
  update(trips: Trip[], version: number): Promise<boolean>;
}

/** Returns the merged trips, now saved in the account. */
export async function syncTrips(local: Trip[], saved: SavedTrips): Promise<Trip[]> {
  for (let attempt = 0; attempt < 5; attempt++) {
    const copy = await saved.read();
    const merged = mergeTrips(local, copy?.trips ?? []);
    if (copy && sameTrips(merged, copy.trips)) return merged;
    if (copy ? await saved.update(merged, copy.version) : await saved.create(merged)) return merged;
  }
  throw new Error('Another device kept saving at the same moment. Try again.');
}
