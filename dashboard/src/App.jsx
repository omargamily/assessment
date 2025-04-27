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
    </Router>
  );
}

export default App;
