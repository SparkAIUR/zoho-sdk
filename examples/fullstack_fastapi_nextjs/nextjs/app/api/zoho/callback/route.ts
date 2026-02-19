// Next.js App Router callback proxy that forwards Zoho callback params to FastAPI.

import { NextRequest, NextResponse } from "next/server";

// --8<-- [start:callback_route]
export async function GET(request: NextRequest): Promise<NextResponse> {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  const backendBase = process.env.ZOHO_BACKEND_URL ?? "http://localhost:8000";

  if (!code || !state) {
    return NextResponse.redirect(new URL("/integrations/zoho?status=invalid_callback", request.url));
  }

  const callbackUrl = new URL(`${backendBase}/oauth/callback`);
  callbackUrl.searchParams.set("code", code);
  callbackUrl.searchParams.set("state", state);

  const response = await fetch(callbackUrl, { method: "GET", cache: "no-store" });
  if (!response.ok) {
    return NextResponse.redirect(new URL("/integrations/zoho?status=failed", request.url));
  }

  const payload = (await response.json()) as { tenant_id?: string };
  const tenant = payload.tenant_id ?? "unknown";

  return NextResponse.redirect(new URL(`/integrations/zoho?status=connected&tenant=${tenant}`, request.url));
}
// --8<-- [end:callback_route]
