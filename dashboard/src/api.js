const API_URL = "http://127.0.0.1:8000/api";

const handleResponse = async (response) => {
  if (response.status === 401) {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// GET requests
export const getUsers = async () => {
  const response = await fetch(`${API_URL}/accounts/users/`);
  return handleResponse(response);
};

export const getPlans = async () => {
  const response = await fetch(`${API_URL}/plans/`);
  return handleResponse(response);
};

// POST requests
export const registerUser = async (userData) => {
  const response = await fetch(`${API_URL}/accounts/register/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  return handleResponse(response);
};

export const signIn = async (credentials) => {
  const response = await fetch(`${API_URL}/accounts/signin/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });
  return handleResponse(response);
};

export const refreshToken = async (token) => {
  const response = await fetch(`${API_URL}/accounts/token/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(token),
  });
  return handleResponse(response);
};

export const createPlan = async (planData) => {
  const response = await fetch(`${API_URL}/plans/create/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(planData),
  });
  return handleResponse(response);
};

export const payInstallment = async ({ id, paymentData }) => {
  const response = await fetch(`${API_URL}/plans/installments/${id}/pay/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(paymentData),
  });
  return handleResponse(response);
};
