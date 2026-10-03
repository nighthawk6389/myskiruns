-- Accounts: each signed-in person's trips, as one record (README, "Accounts").
-- Run once in the Supabase project's SQL editor.
--
-- `trips` is the app's trip list (src/trips/log.ts), merged on the device
-- (src/trips/sync.ts). `version` stops two devices overwriting each other:
-- an update names the version it read, and a device that lost the race reads
-- again and merges again. The row goes with the user (on delete cascade).

create table if not exists public.trip_logs (
  user_id uuid primary key references auth.users (id) on delete cascade,
  trips jsonb not null default '[]'::jsonb,
  version integer not null default 1,
  updated_at timestamptz not null default now(),
  -- a season is a few KB; this only stops a runaway client
  constraint trip_logs_size check (pg_column_size(trips) < 2000000)
);

alter table public.trip_logs enable row level security;

-- signed-in people see and change their own row only; nobody else's, and
-- signed-out visitors nothing
create policy "own trips: read" on public.trip_logs
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "own trips: create" on public.trip_logs
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "own trips: update" on public.trip_logs
  for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "own trips: delete" on public.trip_logs
  for delete to authenticated using ((select auth.uid()) = user_id);

grant select, insert, update, delete on public.trip_logs to authenticated;
