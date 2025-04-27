import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const isAuthenticated =
    localStorage.getItem("access") || localStorage.getItem("refresh");

  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />;
  }

  return (
    <>
      {window.location.href != "/signin" &&
        window.location.href != "/signup" && (
          <button
            onClick={() => {
              localStorage.removeItem("access");
              localStorage.removeItem("refresh");
              window.location.href = "/signin";
            }}
            className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md shadow-md hover:bg-red-600"
          >
            Sign Out
          </button>
        )}
      {children}
    </>
  );
};

export default ProtectedRoute;
