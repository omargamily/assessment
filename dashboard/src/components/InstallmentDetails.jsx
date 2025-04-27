import { useMutation, useQueryClient } from "@tanstack/react-query";
import { payInstallment } from "../api";
import { useCurrentUser } from "../hooks/useCurrentUser";

const InstallmentDetails = ({ installments }) => {
  const queryClient = useQueryClient();
  const { user } = useCurrentUser();

  const isUser = user?.role === "user";

  const mutation = useMutation({
    mutationFn: payInstallment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["userPlans"] });
    },
    onError: (error) => {
      console.error("Payment failed:", error);
    },
  });

  if (!installments || installments.length === 0) {
    return (
      <div className="text-text-secondary">
        Select a date from the calendar with installments to see details.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {installments
        .filter((it) => it.status != "Paid")
        .map((installment) => {
          if (!installment || typeof installment.id === "undefined") {
            console.error("Installment object missing 'id':", installment);
            return (
              <div
                key={installment?.due_date || Math.random()}
                className="text-red-500"
              >
                Invalid installment data (missing ID)
              </div>
            );
          }

          const parts = installment.due_date.split("-").map(Number);
          const dueDate = new Date(parts[0], parts[1] - 1, parts[2]);
          const formattedDate = dueDate.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          });

          const isProcessing =
            mutation.isPending && mutation.variables?.id === installment.id;
          const hasError =
            mutation.isError && mutation.variables?.id === installment.id;

          return (
            <div
              key={installment.id}
              className="bg-background-white p-4 rounded-lg border border-divider"
            >
              <p className="text-text-secondary mb-1">Date: {formattedDate}</p>
              <p className="text-text-secondary mb-4">
                Amount:{" "}
                {new Intl.NumberFormat("en-SA", {
                  style: "currency",
                  currency: "SAR",
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                }).format(installment.amount)}
              </p>
              {isUser && (
                <button
                  className="bg-button-primary-bg hover:bg-button-primary-hover-bg text-button-text-on-blue font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline w-full disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={() =>
                    mutation.mutate({ id: installment.id, paymentData: {} })
                  }
                  disabled={isProcessing}
                >
                  {isProcessing ? "Processing..." : "Pay"}
                </button>
              )}
              {hasError && (
                <p className="text-red-500 text-xs text-center mt-2">
                  Payment failed. Please try again.
                </p>
              )}
            </div>
          );
        })}
    </div>
  );
};

export default InstallmentDetails;
