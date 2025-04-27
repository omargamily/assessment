import HomePage from "./pages/Home.jsx";
import SignInScreen from "./pages/SignIn.jsx";
import SignUpScreen from "./pages/Signup.jsx";
import PlansPage from "./pages/PlansPage.jsx"; // Import the new Plans page
import CreatePlanPage from "./pages/CreatePlan.jsx";

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
    path: "/",
    element: <HomePage />,
    protected: true,
  },
  {
    path: "/plans",
    element: <PlansPage />,
    protected: true,
  },
  {
    path: "/create-plan",
    element: <CreatePlanPage />,
    protected: true,
  },
  {
    path: "*",
    element: <h1>404 Not Found</h1>,
    protected: false,
  },
];

export default routes;
