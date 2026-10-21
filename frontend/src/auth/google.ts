export interface GoogleConfiguration {
  enabled: boolean;
  client_id: string;
}

interface GoogleTokenResponse {
  access_token?: string;
  error?: string;
  error_description?: string;
}

interface GoogleTokenClient {
  requestAccessToken: (overrideConfig?: { prompt?: string }) => void;
}

declare global {
  interface Window {
    google?: {
      accounts?: {
        oauth2?: {
          initTokenClient: (config: {
            client_id: string;
            scope: string;
            prompt?: string;
            callback: (response: GoogleTokenResponse) => void;
            error_callback?: (error: { type?: string; message?: string }) => void;
          }) => GoogleTokenClient;
        };
      };
    };
  }
}

let scriptPromise: Promise<void> | null = null;

function loadGoogleIdentityScript(): Promise<void> {
  if (typeof window !== "undefined" && window.google?.accounts?.oauth2) {
    return Promise.resolve();
  }
  if (scriptPromise) return scriptPromise;

  scriptPromise = new Promise<void>((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      'script[src="https://accounts.google.com/gsi/client"]'
    );
    if (existing) {
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("Failed to load Google script.")), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => {
      scriptPromise = null;
      reject(new Error("Không tải được dịch vụ đăng nhập Google. / Could not load Google Sign-In."));
    };
    document.head.appendChild(script);
  });

  return scriptPromise;
}

export async function requestGoogleAccessToken(clientId: string): Promise<string> {
  await loadGoogleIdentityScript();
  const oauth2 = window.google?.accounts?.oauth2;
  if (!oauth2) {
    throw new Error("Dịch vụ đăng nhập Google chưa sẵn sàng. / Google Sign-In is unavailable.");
  }

  return new Promise<string>((resolve, reject) => {
    const tokenClient = oauth2.initTokenClient({
      client_id: clientId,
      scope: "openid email profile",
      prompt: "select_account",
      callback: (response) => {
        if (response.error || !response.access_token) {
          reject(
            new Error(
              response.error_description ||
                "Đã hủy hoặc không lấy được xác thực từ Google. / Google sign-in was cancelled."
            )
          );
          return;
        }
        resolve(response.access_token);
      },
      error_callback: (err) => {
        if (err?.type === "popup_closed") {
          reject(new Error("Đã đóng cửa sổ đăng nhập Google. / Google sign-in popup was closed."));
        } else {
          reject(new Error(err?.message || "Không thể mở cửa sổ đăng nhập Google."));
        }
      },
    });

    tokenClient.requestAccessToken({ prompt: "select_account" });
  });
}
