// Next.js UI entrypoint for connecting tenant accounts to Zoho.

import Link from "next/link";

// --8<-- [start:connect_ui]
export default async function ZohoIntegrationPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const status = typeof params.status === "string" ? params.status : "idle";
  const tenant = typeof params.tenant === "string" ? params.tenant : "default";

  return (
    <main>
      <h1>Zoho Integration</h1>
      <p>Status: {status}</p>
      <p>Tenant: {tenant}</p>
      <Link href="/api/zoho/connect?tenant=tenant-a">Connect tenant-a</Link>
    </main>
  );
}
// --8<-- [end:connect_ui]
