import { useQuery } from "@tanstack/react-query";
import DashboardHeader from "../components/DashboardHeader";
import PlanDetails from "../components/PlanDetails";
import { getPlans } from "../api";

const DashboardPage = () => {
  const {
    data: plans,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["userPlans"],
    queryFn: getPlans,
  });

  if (isLoading) {
    return (
      <div className="container mx-auto p-4 text-center text-text-secondary">
        Loading plans...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto p-4 text-center text-red-500">
        Error loading plans: {error.message}
      </div>
    );
  }

  const userPlan = plans && plans.length > 0 ? plans[0] : null;

  return (
    <div className="container mx-auto p-4">
      <div className="bg-background-white p-6 rounded-2xl shadow-md mt-6">
        <DashboardHeader />
        <h2 className="text-xl font-semibold text-text-primary border-b border-divider pb-4">
          Plans
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
          <div className="pr-6 md:border-r border-divider">
            {userPlan ? (
              <PlanDetails plan={userPlan} />
            ) : (
              <div className="text-text-secondary mt-6">
                No plan found for this user.
              </div>
            )}
          </div>

          {/* Right Column: Calendar and Installment Details */}
          <div className="pl-6 flex flex-col">
            {" "}
            {/* Left padding for the column */}
            {/* Calendar Section with bottom border */}
            <div className="pb-6 mb-6">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Calendar
              </h3>
              {/* Calendar Component */}
            </div>
            {/* Installment Details Section */}
            {/* <div>
              {" "}
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Installment Details
              </h3>
            </div> */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
