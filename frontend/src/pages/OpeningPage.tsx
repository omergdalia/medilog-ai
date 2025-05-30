import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import {jwtDecode } from "jwt-decode";
import { checkPatientExists } from '../services/apiService';

declare global {
  interface Window {
    google: any;
  }
}

export default function OpeningPage() {
  const navigate = useNavigate();


      
  const handleUserLogin = (email: string) => {
    // Here you can handle the user login logic, e.g., store the email in state or context
    console.log("User logged in with email:", email);
    const userExists = await checkPatientExists(email);
    if(userExists)  {
      console.log("User with email:" + email + " exists, signing in and redirecting to dashboard...");
      // Redirect to dashboard after login

      navigate("/");
    } else {

    navigate("/SignUp"); // Redirect to dashboard after login
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Welcome to My App</h1>
     <GoogleLogin
        onSuccess={(credentialResponse) => {
          const decodedJSON = jwtDecode(credentialResponse.credential);
          handleUserLogin(email);
        }}
        onError={() => console.error("Google Login Error")} />
          
    </div>
  );
}
