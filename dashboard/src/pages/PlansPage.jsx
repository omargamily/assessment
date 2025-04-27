import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom"; // Import Link for navigation
import PlanDetails from "../components/PlanDetails";
import DashboardCalendarGrid from "../components/DashboardCalendarGrid";
import InstallmentDetails from "../components/InstallmentDetails";
import { getPlans } from "../api";
import DashboardContent from "../components/DashboardContent"; // Import DashboardContent

const PlansPage = () => {
  const [selectedInstallmentsList, setSelectedInstallmentsList] = useState([]);

  const {
    data: plans,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["userPlans"],
    queryFn: getPlans,
  });

  // Loading and error states remain the same
  if (isLoading) {
    return (
      <DashboardContent>
        <div className="container mx-auto p-4 text-center text-text-secondary">
          Loading plans...
        </div>
      </DashboardContent>
    );
  }

  if (isError) {
    return (
      <DashboardContent>
        <div className="container mx-auto p-4 text-center text-red-500">
          Error loading plans: {error.message}
        </div>
      </DashboardContent>
    );
  }

  const userPlan = plans && plans.length > 0 ? plans[0] : null;
  const allInstallments = userPlan?.installments || [];

  const handleDateStringSelect = (selectedDateString) => {
    if (selectedDateString) {
      const matchingInstallments = allInstallments.filter(
        (inst) => inst.due_date === selectedDateString
      );
      setSelectedInstallmentsList(matchingInstallments);
    } else {
      setSelectedInstallmentsList([]);
    }
  };

  return (
    <DashboardContent>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-0 mt-6">
        {/* Plan Details */}
        <div className="pr-6 md:border-r border-divider">
          {userPlan ? (
            <PlanDetails plan={userPlan} />
          ) : (
            <div className="text-text-secondary mt-6">
              No plan found for this user. Consider adding a 'Create Plan'
              button here.
            </div>
          )}
        </div>

        {/* Calendar and Installment Details */}
        <div className="pl-6 flex flex-col">
          <div className="pb-6 my-6 border-b border-divider">
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Calendar
            </h3>
            <DashboardCalendarGrid
              installments={allInstallments}
              onDateStringSelect={handleDateStringSelect}
            />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Installment Details
            </h3>
            <InstallmentDetails installments={selectedInstallmentsList} />
          </div>
        </div>
      </div>
    </DashboardContent>
  );
};

export default PlansPage;
