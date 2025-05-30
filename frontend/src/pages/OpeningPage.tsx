import { useNavigate } from "react-router-dom";
import { useGoogleLogin, type TokenResponse as GoogleApiTokenResponse } from "@react-oauth/google";
import { checkPatientExists, signInUser } from '../services/apiService'; // Assuming these are correctly defined
import { useLocalStorage } from "../hooks/useLocalStorage";

// Kept as per your original code; may or may not be strictly necessary with @react-oauth/google
declare global {
  interface Window {
    google: any;
  }
}

// SVG for Google Icon (no changes here)
const GoogleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="24px" height="24px">
    <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
    <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
    <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
    <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.574l6.19,5.238C39.712,35.619,44,29.57,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
  </svg>
);

export default function OpeningPage() {
  const navigate = useNavigate();
  const [, setUserEmail] = useLocalStorage("userEmail", "");

  const decodeJwtResponse = (token: string): { email?: string; [key: string]: any } => {
    try {
      const base64Url = token.split('.')[1];
      if (!base64Url) return {};
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error("Error decoding JWT:", error);
      return {};
    }
  };

  const handleUserLoginLogic = async (email: string) => {
    try {
      console.log("Processing login for email:", email);
      const userExists = await checkPatientExists(email);
      if (userExists) {
        console.log("User exists, signing in...");
        await signInUser(email);
        setUserEmail(email);
        navigate("/");
      } else {
        console.log("User does not exist, navigating to signup.");
        setUserEmail(email); // Pre-fill email for signup if desired
        navigate("/SignUp"); // Ensure this route matches your router setup
      }
    } catch (error) {
      console.error("Error during user login processing:", error);
      // TODO: Show user-facing error message
    }
  };

  const googleAuthLogin = useGoogleLogin({
    onSuccess: async (tokenResponse: Omit<GoogleApiTokenResponse, 'error' | 'error_description' | 'error_uri'>) => {
      console.log("Google token response:", tokenResponse);
      let email: string | undefined = undefined;

      try {
        // Prefer email from ID token if available
        if (tokenResponse.id_token) {
          console.log("Attempting to decode ID token");
          const decodedIdToken = decodeJwtResponse(tokenResponse.id_token);
          email = decodedIdToken?.email;
          if(email) console.log("Email from ID token:", email);
        }

        // Fallback to userinfo endpoint if email not in id_token or id_token not present
        if (!email && tokenResponse.access_token) {
          console.log("Email not found in ID token or ID token missing, fetching from userinfo endpoint.");
          const userInfoResponse = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
            headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
          });

          if (!userInfoResponse.ok) {
            const errorData = await userInfoResponse.text();
            console.error("Failed to fetch user info:", userInfoResponse.status, errorData);
            throw new Error(`Failed to fetch user info. Status: ${userInfoResponse.status}`);
          }
          const userInfo = await userInfoResponse.json();
          email = userInfo?.email;
          
          if(email)
            {
              localStorage.setItem("userEmail", email || "");
              console.log("Email from userinfo endpoint:", email);
            }
        }

        if (email) {
          await handleUserLoginLogic(email);
        } else {
          console.error("Could not retrieve email from Google authentication.");
          // TODO: Show user-facing error message
        }
      } catch (error) {
        console.error("Error processing Google login:", error);
        // TODO: Show user-facing error message
      }
    },
    onError: (errorResponse) => {
      console.error("Google Login Error:", errorResponse);
      // TODO: Show user-facing error message
    },
    // flow: 'implicit' // This is the default, provides access_token and potentially id_token
  });

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-sky-100 to-indigo-200 p-4 sm:p-6">
      <div className="w-full max-w-md bg-white/80 backdrop-blur-lg rounded-xl shadow-xl p-8 sm:p-10 border border-slate-300/70">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-indigo-700 mb-3 text-center">
          Welcome to <span className="text-sky-600">MediLogAI</span>
        </h1>
        <p className="text-slate-500 text-md sm:text-lg mb-8 text-center">
          Your smart companion for tracking symptoms and prepping doctor visits.
        </p>

        <div className="mt-8">
          <button
            onClick={() => googleAuthLogin()} // This calls the function from useGoogleLogin
            type="button"
            className="w-full py-3 px-4 rounded-lg bg-white hover:bg-slate-50 text-slate-700 font-medium border border-slate-300 flex items-center justify-center space-x-3 transition-colors duration-150 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <GoogleIcon />
            <span>Sign in with Google</span>
          </button>
        </div>
      </div>
    </div>
  );
}