// Vercel function: DELETE /api/account (see api/_lib/account.ts).
//
// Needs the Supabase project's URL, public key and service key in the
// project's environment variables (README, "Accounts"). Without them the
// endpoint answers 503.
// Relative imports in api/ need their .js extension: Vercel runs these files
// as Node ESM (package.json "type": "module"), which won't resolve bare paths.
import { accountEnv, handleAccount } from './_lib/account.js';

export async function DELETE(req: Request) {
  return handleAccount(req, accountEnv(process.env));
}
