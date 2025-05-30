import { useState } from "react";

export default function SignupPage() {
  const [age, setAge] = useState<number | undefined>();
  const [gender, setGender] = useState("");
  const [allergies, setAllergies] = useState([""]);
  const [diseases, setDiseases] = useState([""]);
  const [medications, setMedications] = useState([""]);
  const userEmail = localStorage.getItem("userEmail") || "";

  const handleListChange = (
    setter: React.Dispatch<React.SetStateAction<string[]>>,
    index: number,
    value: string
  ) => {
    setter((prev) => {
      const updated = [...prev];
      updated[index] = value;
      return updated;
    });
  };

  const addField = (setter: React.Dispatch<React.SetStateAction<string[]>>) => {
    setter((prev) => [...prev, ""]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      'mail': userEmail,
      age,
      gender,
      allergies: allergies.filter((a) => a.trim() !== ""),
      chronic_diseases: diseases.filter((d) => d.trim() !== ""),
      medications: medications.filter((m) => m.trim() !== ""),
    };

    try {
      const res = await fetch(`${process.env.API_BASE}/api/auth/complete_signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      console.log("Signup success:", data);
      // Redirect or show success
    } catch (error) {
      console.error("Signup error:", error);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center bg-gray-50 p-4">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md w-full max-w-md space-y-4">
        <h2 className="text-2xl font-bold mb-4 text-center">Complete Your Profile</h2>


    <input
      type="text"
      inputMode="numeric"
      pattern="[0-9]*"
      value={age}
      onChange={(e) => {
        const val = e.target.value;
        // Allow only digits or empty input
        if (/^\d*$/.test(val)) {
          setAge(val);
        }
      }}
      placeholder="Age"
      className="w-full p-2 border rounded appearance-none"
    />

        <select
          value={gender}
          onChange={(e) => setGender(e.target.value)}
          className="w-full p-2 border rounded"
          required
        >
          <option value="">Select Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>

        {/* Allergies */}
<div className="relative flex flex-col">
  <label className="font-semibold mb-2">Allergies</label>
  {allergies.map((val, i) => (
    <div key={i} className="relative flex items-center">
      <input
        type="text"
        value={val}
        onChange={(e) => handleListChange(setAllergies, i, e.target.value)}
        className="w-full p-2 mt-1 mb-2 border rounded"
        placeholder={`Allergy ${i + 1}`}
      />
      {allergies.length > 1 && i !== allergies.length - 1 && (
        <button
          type="button"
          onClick={() => setAllergies((prev) => prev.filter((_, index) => index !== i))}
          className="absolute bottom-0 right-0 bg-transparent text-blue-600 text-xl font-bold w-8"
        >
          -
        </button>
      )}
    </div>
  ))}
  <button
    type="button"
    onClick={() => addField(setAllergies)}
    className="absolute bottom-0 right-0 bg-transparent text-blue-600 text-xl font-bold w-8"
  >
    +
  </button>
</div>

{/* Chronic Diseases */}
<div className="relative flex flex-col">
  <label className="font-semibold mb-2">Chronic Diseases</label>
  {diseases.map((val, i) => (
    <div key={i} className="relative flex items-center">
      <input
        type="text"
        value={val}
        onChange={(e) => handleListChange(setDiseases, i, e.target.value)}
        className="w-full p-2 mt-1 mb-2 border rounded"
        placeholder={`Disease ${i + 1}`}
      />
      {diseases.length > 1 && i !== diseases.length - 1 && (
        <button
          type="button"
          onClick={() => setDiseases((prev) => prev.filter((_, index) => index !== i))}
          className="absolute bottom-0 right-0 bg-transparent text-blue-600 text-xl font-bold w-8"
        >
          -
        </button>
      )}
    </div>
  ))}
  <button
    type="button"
    onClick={() => addField(setDiseases)}
    className="absolute bottom-0 right-0 bg-transparent text-blue-600 text-xl font-bold w-8"
  >
    +
  </button>
</div>

{/* Medications */}
<div className="relative flex flex-col">
  <label className="font-semibold mb-2">Medications</label>
  {medications.map((val, i) => (
    <div key={i} className="relative flex items-center">
      <input
        type="text"
        value={val}
        onChange={(e) => handleListChange(setMedications, i, e.target.value)}
        className="w-full p-2 mt-1 mb-2 border rounded"
        placeholder={`Medication ${i + 1}`}
      />
      {medications.length > 1 && i !== medications.length - 1 && (
        <button
          type="button"
          onClick={() => setMedications((prev) => prev.filter((_, index) => index !== i))}
          className="absolute bottom-0 right-0 bg-transparent text-blue-600 text-xl font-bold w-8"
        >
          -
        </button>
      )}
    </div>
  ))}
  <button
    type="button"
    onClick={() => addField(setMedications)}
    className="absolute bottom-0 right-0 bg-transparent text-blue-600 text-xl font-bold w-8"
  >
    +
  </button>
</div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white p-2 rounded mt-4"
        >
          Submit
        </button>
      </form>
    </div>
  );
}
