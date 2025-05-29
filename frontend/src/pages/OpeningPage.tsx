import React, { useState } from 'react';

export default function OpeningPage() {
  const [showSignup, setShowSignup] = useState(false);
  const [showLogin, setShowLogin] = useState(false);

  const handleGoogleSignUp = () => {
    // Trigger Google OAuth popup here
    // Example: using Google Identity Services
    window.google.accounts.id.prompt(); // Simplified
  };

  const handleSignupSubmit = (e) => {
    e.preventDefault();
    // Send age, gender, etc., and ID token to your backend
  };

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    // Validate with your backend (email + password)
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-3xl font-bold mb-6">Welcome to My App</h1>
      <div className="space-x-4">
        <button
          onClick={() => setShowSignup(true)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg"
        >
          Sign Up
        </button>
        <button
          onClick={() => setShowLogin(true)}
          className="px-6 py-2 bg-green-600 text-white rounded-lg"
        >
          Log In
        </button>
      </div>

      {/* Sign Up Modal */}
      {showSignup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-6 rounded-lg w-full max-w-sm">
            <h2 className="text-xl font-bold mb-4">Sign Up with Google</h2>
            <button
              onClick={handleGoogleSignUp}
              className="mb-4 bg-red-500 text-white px-4 py-2 rounded"
            >
              Sign in with Google
            </button>
            <form onSubmit={handleSignupSubmit} className="space-y-2">
              <input type="number" placeholder="Age" className="w-full p-2 border rounded" />
              <select className="w-full p-2 border rounded">
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
              <button
                type="submit"
                className="w-full bg-blue-600 text-white p-2 rounded"
              >
                Submit
              </button>
              <button
                type="button"
                onClick={() => setShowSignup(false)}
                className="w-full bg-gray-300 p-2 rounded mt-2"
              >
                Cancel
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Log In Modal */}
      {showLogin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-6 rounded-lg w-full max-w-sm">
            <h2 className="text-xl font-bold mb-4">Log In</h2>
            <form onSubmit={handleLoginSubmit} className="space-y-2">
              <input type="email" placeholder="Google Email" className="w-full p-2 border rounded" />
              <input type="password" placeholder="Password" className="w-full p-2 border rounded" />
              <button
                type="submit"
                className="w-full bg-green-600 text-white p-2 rounded"
              >
                Log In
              </button>
              <button
                type="button"
                onClick={() => setShowLogin(false)}
                className="w-full bg-gray-300 p-2 rounded mt-2"
              >
                Cancel
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
