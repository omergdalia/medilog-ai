import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { checkPatientExists, signInUser } from '../services/apiService';
import { useLocalStorage } from "../hooks/useLocalStorage";

export default function OpeningPage() {
  const navigate = useNavigate();
  const [, setUserEmail] = useLocalStorage("userEmail", ""); // destructure setter

  const decodeJwtResponse = (token: string) => {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  };

  const handleUserLogin = async (email: string) => {
    try {
      console.log("User logged in with email:", email);
      const userExists = await checkPatientExists(email);
      if (userExists) {
        console.log("User exists, signing in...");
        await signInUser(email);
        setUserEmail(email); // Store email in local storage
        navigate("/");
      } else {
        navigate("/SignUp");
      }
    } catch (error) {
      console.error("Error during user login:", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Welcome to My App</h1>
      <GoogleLogin
        onSuccess={(credentialResponse) => {
          if (credentialResponse.credential) {
            const email = decodeJwtResponse(credentialResponse.credential).email;
            handleUserLogin(email);
          } else {
            console.error("No credential received");
          }
        }}
        onError={() => console.error("Google Login Error")}
      />
    </div>
  );
}
