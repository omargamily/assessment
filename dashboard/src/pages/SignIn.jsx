import { useMutation } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { signIn } from "../api.js";

const SignInScreen = () => {
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: signIn,
    onSuccess: (data) => {
      console.log("Sign-in successful:", data);
      if (data && data.accessToken && data.refreshToken) {
        localStorage.setItem("accessToken", data.accessToken);
        localStorage.setItem("refreshToken", data.refreshToken);
        console.log("Tokens saved to local storage!");
        navigate("/dashboard");
      } else {
        console.warn("Sign-in successful but no tokens received in service.");
      }
    },
    onError: (error) => {
      console.error("Sign-in failed in service:", error);
      throw error;
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    const email = e.target.email.value;
    const password = e.target.password.value;

    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }
    mutation.mutate({ email, password });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-background-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h2 className="text-3xl font-semibold text-text-primary text-center mb-6">
          Sign In
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

          <div className="mb-6">
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

          <div className="flex items-center justify-center">
            <button
              type="submit"
              className="bg-button-primary-bg hover:bg-button-primary-hover-bg text-button-text-on-blue font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline w-full"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Signing In..." : "Sign In"}
            </button>
          </div>

          {mutation.isError && (
            <p className="text-red-500 text-center mt-4">
              Error: {mutation.error.message || "An unknown error occurred."}
            </p>
          )}
        </form>
        <Link
          to="/signup"
          className="text-sm text-center text-text-secondary mt-4 block"
        >
          Don&apos;t have an account? Sign Up
        </Link>
      </div>
    </div>
  );
};

export default SignInScreen;
