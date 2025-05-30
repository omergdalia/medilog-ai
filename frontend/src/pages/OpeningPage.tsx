import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

declare global {
  interface Window {
    google: any;
  }
}

export default function OpeningPage() {
  const navigate = useNavigate();

  useEffect(() => {
    if (!window.google || !window.google.accounts) {
      console.error("Google Identity Services library not loaded.");
      return;
    }

    window.google.accounts.id.initialize({
    client_id: process.env.GOOGLE_CLIENT_ID,
    callback: handleCredentialResponse,
    });
  }, []);

  const handleCredentialResponse = async (response: any) => {
    const idToken = response.credential;

    try {
      const res = await fetch("/api/auth/google", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idToken }),
      });

      const data = await res.json();

      if (data.exists) {
        // Redirect to dashboard or main app
        console.log("Login success:", data.user);
        navigate("/dashboard");
      } else {
        // Redirect to sign-up page
        console.log("User not registered, redirecting to sign-up");
        navigate("/signup");
      }
    } catch (error) {
      console.error("Authentication error:", error);
    }
  };

  const handleGoogleSignIn = () => {
    if (!window.google || !window.google.accounts) {
      console.error("Google Identity Services not ready.");
      return;
    }

    // Trigger the prompt
    window.google.accounts.id.prompt((notification: any) => {
      if (notification.isNotDisplayed()) {
        console.error("Prompt not displayed:", notification.reason);
      } else if (notification.isSkippedMoment()) {
        console.log("Prompt skipped:", notification.reason);
      } else if (notification.isDismissedMoment()) {
        console.log("Prompt dismissed.");
      }
    });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Welcome to My App</h1>
      <button
        onClick={handleGoogleSignIn}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg"
      >
        Continue with Google
      </button>
    </div>
  );
}
