import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import routes from "./routes.jsx";

export const PageWithHeader = ({ children }) => (
  <div className="flex h-full flex-col">{children}</div>
);

function App() {
  return (
    <Router>
      <div className="bg-gray-50 min-h-screen">
        <Routes>
          {routes.map((route, index) => {
            if (route.protected) {
              return (
                <Route
                  key={index}
                  path={route.path}
                  element={<ProtectedRoute>{route.element}</ProtectedRoute>}
                />
              );
            }
            return (
              <Route key={index} path={route.path} element={route.element} />
            );
          })}
        </Routes>
      </div>
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
    </Router>
  );
}

export default App;
