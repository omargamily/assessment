import PropTypes from "prop-types";
import { Link, useLocation } from "react-router-dom";

const DashboardContent = ({ title, children }) => {
  const location = useLocation();
  return (
    <div className="p-6 rounded-2xl mt-6 ">
      <div className="bg-background-white p-6 rounded-2xl shadow-md w-3/5 mx-auto">
        <h2 className="text-xl font-semibold text-text-primary pb-4">
          {title}
        </h2>

        <nav className="mb-6 border-b border-divider py-2">
          <ul className="flex space-x-4">
            <li>
              <Link
                to="/plans"
                className={`text-gray-600 hover:text-gray-800 border-b-2 ${location.pathname === "/plans" ? "border-blue-500" : "border-transparent"} py-2 px-4 transition-colors duration-200`}
              >
                Plans
              </Link>
            </li>
            <li>
              <Link
                to="/home"
                className={`text-gray-600 hover:text-gray-800 border-b-2 ${location.pathname === "/home" ? "border-blue-500" : "border-transparent"} py-2 px-4 transition-colors duration-200`}
              >
                Home
              </Link>
            </li>
          </ul>
        </nav>
        <div>{children}</div>
      </div>
    </div>
  );
};

DashboardContent.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};

export default DashboardContent;
