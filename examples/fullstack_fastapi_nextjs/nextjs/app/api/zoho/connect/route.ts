// Next.js App Router route for initiating tenant OAuth with the FastAPI backend.

import { NextRequest, NextResponse } from "next/server";

// --8<-- [start:connect_route]
export async function GET(request: NextRequest): Promise<NextResponse> {
  const tenantId = request.nextUrl.searchParams.get("tenant") ?? "default";
  const backendBase = process.env.ZOHO_BACKEND_URL ?? "http://localhost:8000";

  const response = await fetch(`${backendBase}/oauth/${tenantId}/start`, {
    method: "GET",
    cache: "no-store",
  });

  if (!response.ok) {
    return NextResponse.json({ error: "oauth_start_failed" }, { status: 502 });
  }

  const payload = (await response.json()) as { authorize_url?: string };
  if (!payload.authorize_url) {
    return NextResponse.json({ error: "missing_authorize_url" }, { status: 500 });
  }

  return NextResponse.redirect(payload.authorize_url);
}
// --8<-- [end:connect_route]
