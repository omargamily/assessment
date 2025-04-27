import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom"; // Import Link
import { registerUser } from "../api.js";

const SignUpScreen = () => {
  const [role, setRole] = useState("");
  const navigate = useNavigate();

  const handleRoleChange = (event) => {
    setRole(event.target.value);
  };

  const mutation = useMutation({
    mutationFn: registerUser,
    onSuccess: (data) => {
      if (data && data.accessToken && data.refreshToken) {
        localStorage.setItem("access", data.accessToken);
        localStorage.setItem("refresh", data.refreshToken);
        navigate("/dashboard");
      } else {
        navigate("/signin");
      }
    },
    onError: (error) => {
      console.error("Registration failed in service:", error);
      throw error;
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    const email = e.target.email.value;
    const password = e.target.password.value;

    mutation.mutate({ email, password, role });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-background-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h2 className="text-3xl font-semibold text-text-primary text-center mb-6">
          Sign Up
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="email"
              className="block text-text-secondary text-sm font-semibold mb-2"
            >
              Email
            </label>
            <input
              type="email"
              id="email"
              className="appearance-none border border-border-default rounded-lg w-full py-2 px-3 text-text-primary leading-tight focus:outline-none focus:ring-input-focus focus:border-input-focus"
              required
            />
          </div>

          <div className="mb-4">
            <label
              htmlFor="password"
              className="block text-text-secondary text-sm font-semibold mb-2"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              className="appearance-none border border-border-default rounded-lg w-full py-2 px-3 text-text-primary leading-tight focus:outline-none focus:ring-input-focus focus:border-input-focus"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-text-secondary text-sm font-semibold mb-2">
              Role
            </label>
            <div className="flex items-center">
              <input
                type="radio"
                id="merchant"
                name="role"
                value="merchant"
                className="appearance-none mr-2 w-5 h-5 border border-border-secondary rounded-sm checked:bg-button-primary-bg checked:border-button-primary-bg focus:outline-none focus:ring-input-focus focus:ring-offset-2"
                checked={role === "merchant"}
                onChange={handleRoleChange}
              />
              <label htmlFor="merchant" className="text-text-secondary mr-4">
                Merchant
              </label>

              <input
                type="radio"
                id="user"
                name="role"
                value="user"
                className="appearance-none mr-2 w-5 h-5 border border-border-secondary rounded-sm checked:bg-button-primary-bg checked:border-button-primary-bg focus:outline-none focus:ring-input-focus focus:ring-offset-2"
                checked={role === "user"}
                onChange={handleRoleChange}
              />
              <label htmlFor="user" className="text-text-secondary">
                User
              </label>
            </div>
          </div>

          <div className="flex items-center justify-center">
            <button
              type="submit"
              className="bg-button-primary-bg hover:bg-button-primary-hover-bg text-button-text-on-blue font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline w-full"
            >
              Sign Up
            </button>
          </div>
        </form>
        <Link
          to="/signin"
          className="text-sm text-center text-text-secondary mt-4 block"
        >
          Already have an account? Sign In
        </Link>
      </div>
    </div>
  );
};

export default SignUpScreen;
