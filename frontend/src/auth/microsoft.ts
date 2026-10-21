import type { AuthenticationResult, PublicClientApplication } from "@azure/msal-browser";
export type MicrosoftConfiguration = { enabled: boolean; client_id: string; tenant_id: string };
let instance: Promise<PublicClientApplication> | undefined;
let redirectResult: Promise<AuthenticationResult | null> | undefined;
export const MICROSOFT_PENDING = "eduface_microsoft_pending";

export function safeReturnPath(path: unknown): string {
  return typeof path === "string" && path.startsWith("/") && !path.startsWith("//") && !/[\\\u0000-\u001f]/.test(path) && !path.startsWith("/login") ? path : "/";
}
export function microsoftClient(config: MicrosoftConfiguration): Promise<PublicClientApplication> {
  if (!instance) instance = import("@azure/msal-browser").then(async ({ PublicClientApplication }) => {
    const client = new PublicClientApplication({
      auth: { clientId: config.client_id, authority: `https://login.microsoftonline.com/${config.tenant_id}`, redirectUri: `${window.location.origin}/microsoft-redirect.html` },
      cache: { cacheLocation: "sessionStorage" },
    });
    await client.initialize(); return client;
  }).catch((error) => { instance = undefined; throw error; });
  return instance;
}
export function handleMicrosoftRedirect(config: MicrosoftConfiguration) {
  if (!redirectResult) redirectResult = microsoftClient(config).then((client) => client.handleRedirectPromise());
  return redirectResult;
}
