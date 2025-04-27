import DashboardPage from "./pages/Dashboard.jsx";
import SignInScreen from "./pages/SignIn.jsx";
import SignUpScreen from "./pages/Signup.jsx";

const routes = [
  {
    path: "/signup",
    element: <SignUpScreen />,
    protected: false,
  },
  {
    path: "/signin",
    element: <SignInScreen />,
    protected: false,
  },
  {
    path: "/dashboard",
    element: <DashboardPage />,
    protected: true,
  },
  {
    path: "*",
    element: <h1>404 Not Found</h1>,
    protected: false,
  },
];

export default routes;
