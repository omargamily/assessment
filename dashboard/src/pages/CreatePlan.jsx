import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { getUsers, createPlan } from "../api";
import DashboardContent from "../components/DashboardContent";

const CreatePlanPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [selectedUser, setSelectedUser] = useState("");
  const [amount, setAmount] = useState("");
  const [installments, setInstallments] = useState("");
  const [startDate, setStartDate] = useState("");

  const {
    data: usersData,
    isLoading: isLoadingUsers,
    isError: isErrorUsers,
    error: errorUsers,
  } = useQuery({
    queryKey: ["users"],
    queryFn: getUsers,
  });

  const mutation = useMutation({
    mutationFn: createPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["userPlans"] });
      navigate("/plans"); // Navigate back to plans list on success
    },
    onError: (error) => {
      console.error("Failed to create plan:", error);
      // Display error to user maybe?
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedUser || !amount || !installments || !startDate) {
      alert("Please fill in all fields."); // Basic validation
      return;
    }

    const planData = {
      user: selectedUser, // Assuming selectedUser holds the ID
      total_amount: String(amount), // Ensure amount is a string
      number_of_installments: Number(installments), // Ensure installments is a number
      start_date: startDate,
    };

    mutation.mutate(planData);
  };

  return (
    <DashboardContent title="Create New Plan">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="user"
            className="block text-sm font-medium text-text-secondary"
          >
            Select User
          </label>
          <select
            id="user"
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
            className="mt-1 block w-full rounded-lg border-border-default shadow-sm focus:border-input-focus focus:ring focus:ring-input-focus focus:ring-opacity-50 py-2 px-3 text-text-primary"
            required
            disabled={isLoadingUsers || isErrorUsers}
          >
            <option value="" disabled>
              {isLoadingUsers
                ? "Loading users..."
                : isErrorUsers
                  ? `Error: ${errorUsers?.message || "Could not load users"}`
                  : "-- Select a User --"}
            </option>
            {usersData?.map((user) => (
              // Assuming user object has 'id' and 'email'
              <option key={user.id} value={user.id}>
                {user.email}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="amount"
            className="block text-sm font-medium text-text-secondary"
          >
            Total Amount (SAR)
          </label>
          <input
            type="number"
            id="amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="mt-1 block w-full rounded-lg border-border-default shadow-sm focus:border-input-focus focus:ring focus:ring-input-focus focus:ring-opacity-50 py-2 px-3 text-text-primary"
            required
            min="0.01"
            step="0.01"
            placeholder="e.g., 1000.00"
          />
        </div>

        <div>
          <label
            htmlFor="installments"
            className="block text-sm font-medium text-text-secondary"
          >
            Number of Installments
          </label>
          <input
            type="number"
            id="installments"
            value={installments}
            onChange={(e) => setInstallments(e.target.value)}
            className="mt-1 block w-full rounded-lg border-border-default shadow-sm focus:border-input-focus focus:ring focus:ring-input-focus focus:ring-opacity-50 py-2 px-3 text-text-primary"
            required
            min="1"
            step="1"
            placeholder="e.g., 4"
          />
        </div>

        <div>
          <label
            htmlFor="start-date"
            className="block text-sm font-medium text-text-secondary"
          >
            Start Date
          </label>
          <input
            type="date"
            id="start-date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="mt-1 block w-full rounded-lg border-border-default shadow-sm focus:border-input-focus focus:ring focus:ring-input-focus focus:ring-opacity-50 py-2 px-3 text-text-primary"
            required
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="bg-button-primary-bg hover:bg-button-primary-hover-bg text-button-text-on-blue font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline disabled:opacity-50"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Creating Plan..." : "Create Plan"}
          </button>
        </div>
        {mutation.isError && (
          <p className="text-red-500 text-center mt-2">
            Failed to create plan: {mutation.error?.message || "Unknown error"}
          </p>
        )}
      </form>
    </DashboardContent>
  );
};

export default CreatePlanPage;
