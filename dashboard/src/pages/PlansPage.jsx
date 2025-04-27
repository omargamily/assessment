import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import PlanDetails from "../components/PlanDetails";
import DashboardCalendarGrid from "../components/DashboardCalendarGrid";
import InstallmentDetails from "../components/InstallmentDetails";
import { getPlans } from "../api";
import DashboardContent from "../components/DashboardContent";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

const PlansPage = () => {
  const [selectedPlan, setSelectedPlan] = useState(null);
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

  useEffect(() => {
    if (plans && plans.length > 0 && !selectedPlan) {
      setSelectedPlan(plans[0]);
    }
  }, [plans, selectedPlan]);

  if (isLoading) {
    return (
      <DashboardContent title="Plans">
        <div className="container mx-auto p-4 text-center text-text-secondary">
          Loading plans...{" "}
          <span role="img" aria-label="loading">
            ⏳
          </span>
        </div>
      </DashboardContent>
    );
  }

  if (isError) {
    return (
      <DashboardContent title="Plans">
        <div className="container mx-auto p-4 text-center text-red-500">
          Error loading plans: {error.message}{" "}
          <span role="img" aria-label="error">
            ❌
          </span>
        </div>
      </DashboardContent>
    );
  }

  const allInstallments = selectedPlan?.installments || [];

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

  const handlePlanSelect = (plan) => {
    setSelectedPlan(plan);
    setSelectedInstallmentsList([]);
  };

  return (
    <DashboardContent title="Your Plans">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        <div className="md:col-span-1 pr-6 md:border-r border-divider">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Select a Plan
          </h3>
          {plans && plans.length > 0 ? (
            <div className="flex flex-col space-y-2 overflow-y-auto max-h-[60vh]">
              {plans.map((plan) => (
                <button
                  key={plan.id}
                  onClick={() => handlePlanSelect(plan)}
                  className={classNames(
                    "p-3 rounded-lg text-left w-full border transition-colors duration-150",
                    selectedPlan?.id === plan.id
                      ? "bg-blue-100 border-blue-300 ring-1 ring-blue-300"
                      : "bg-background-white border-divider hover:bg-gray-50"
                  )}
                >
                  <p className="text-sm font-medium text-text-primary">
                    {plan.user_email}
                  </p>
                  <p className="text-xs text-text-secondary">
                    {plan?.installments?.length} Installments
                  </p>
                  <p className="text-xs text-text-secondary">
                    Total:{" "}
                    {Number(plan?.total_amount).toLocaleString("en-US", {
                      style: "currency",
                      currency: "SAR",
                    })}
                  </p>
                </button>
              ))}
            </div>
          ) : (
            <div className="text-text-secondary mt-6">
              No plans found.{" "}
              <span role="img" aria-label="sad">
                😔
              </span>
            </div>
          )}
        </div>

        <div className="md:col-span-2 flex flex-col">
          {selectedPlan ? (
            <>
              <div className="pb-6 mb-6 border-b border-divider">
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Installment Calendar
                  <span role="img" aria-label="calendar">
                    📅
                  </span>
                </h3>
                <DashboardCalendarGrid
                  installments={allInstallments}
                  onDateStringSelect={handleDateStringSelect}
                />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Installment Details for Selected Date
                </h3>
                <InstallmentDetails installments={selectedInstallmentsList} />
              </div>
            </>
          ) : (
            <div className="text-text-secondary flex items-center justify-center h-full">
              Please select a plan from the list to view details.{" "}
              <span role="img" aria-label="point left">
                👈
              </span>
            </div>
          )}
        </div>
      </div>
    </DashboardContent>
  );
};

export default PlansPage;
