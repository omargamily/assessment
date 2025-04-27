const InstallmentDetails = ({ installments }) => {
  if (!installments || installments.length === 0) {
    return (
      <div className="text-text-secondary">
        Select a date from the calendar with installments to see details.
      </div>
    );
  }
  console.log("Installments:", installments);

  return (
    <div className="space-y-4">
      {installments.map((installment, index) => {
        const parts = installment.due_date.split("-").map(Number);
        const dueDate = new Date(parts[0], parts[1] - 1, parts[2]);
        const formattedDate = dueDate.toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
        });

        return (
          <div
            key={index}
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
            <button className="bg-button-primary-bg hover:bg-button-primary-hover-bg text-button-text-on-blue font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline w-full">
              Pay
            </button>
          </div>
        );
      })}
    </div>
  );
};

export default InstallmentDetails;
