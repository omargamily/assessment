import PropTypes from "prop-types";

const PlanDetails = ({ plan }) => {
  return (
    <div className="bg-background-white p-4 rounded-lg border border-divider my-6">
      <p className="text-text-primary text-xl text-center mb-4">
        {plan?.user_email}
      </p>
      <p className="text-text-secondary mb-3">
        {plan?.installments?.length?.toLocaleString()} Installments
      </p>
      <p className="text-text-secondary mb-3">Total Amount</p>
      <p className="text-xl font-bold text-text-primary">
        {Number(plan?.total_amount).toLocaleString("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
          style: "currency",
          currency: "SAR",
        })}
      </p>
    </div>
  );
};

PlanDetails.propTypes = {
  plan: PropTypes.shape({
    user_email: PropTypes.string.isRequired,
    installments: PropTypes.array,
    totalAmount: PropTypes.string,
  }).isRequired,
};
export default PlanDetails;
