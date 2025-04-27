const API_URL = "http://127.0.0.1:8000/api";

const getAccessToken = () => localStorage.getItem("access");
const getRefreshToken = () => localStorage.getItem("refresh");
const setAccessToken = (token) => localStorage.setItem("access", token);
const setRefreshToken = (token) => localStorage.setItem("refresh", token);

const clearTokens = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};

const processResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

const isTokenExpiredError = async (response) => {
  const clonedResponse = response.clone();
  try {
    const error = await clonedResponse.json();
    return (
      (response.status === 401 || response.status === 403) &&
      error.messages?.some(({ message }) => message == "Token is expired")
    );
  } catch (e) {
    console.log("Error parsing response:", e);

    return false;
  }
};

const refreshAccessToken = async () => {
  const refresh = getRefreshToken();
  if (!refresh) {
    clearTokens();
    throw new Error("No refresh token available");
  }

  try {
    const response = await fetch(`${API_URL}/accounts/token/refresh/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getAccessToken()}`,
      },
      body: JSON.stringify({ refresh: refresh }),
    });

    if (!response.ok) {
      clearTokens();
      const error = await response.json();
      throw new Error(error.message || "Could not refresh token");
    }

    const data = await response.json();
    setAccessToken(data.access);
    return data.access;
  } catch (error) {
    clearTokens();
    throw error;
  }
};

const fetchAuthenticated = async (url, options = {}) => {
  const acess = getAccessToken();
  const authHeaders = acess ? { Authorization: `Bearer ${acess}` } : {};

  const requestOptions = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
      ...authHeaders,
    },
  };

  let response = await fetch(url, requestOptions);

  if (await isTokenExpiredError(response)) {
    const newAccessToken = await refreshAccessToken();

    const retryOptions = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
        Authorization: `Bearer ${newAccessToken}`,
      },
    };
    response = await fetch(url, retryOptions);
    if (await isTokenExpiredError(response)) {
      clearTokens();
      throw new Error("Refresh token expired or invalid");
    }
  }

  return processResponse(response);
};

export const getUsers = async () => {
  return fetchAuthenticated(`${API_URL}/accounts/users/`);
};

export const getPlans = async () => {
  return fetchAuthenticated(`${API_URL}/plans/`);
};

export const createPlan = async (planData) => {
  return fetchAuthenticated(`${API_URL}/plans/create/`, {
    method: "POST",
    body: JSON.stringify(planData),
  });
};

export const payInstallment = async ({ id, paymentData }) => {
  return fetchAuthenticated(`${API_URL}/plans/installments/${id}/pay/`, {
    method: "POST",
    body: JSON.stringify(paymentData),
  });
};

export const registerUser = async (userData) => {
  const response = await fetch(`${API_URL}/accounts/register/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  });
  return processResponse(response);
};

export const signIn = async (credentials) => {
  const response = await fetch(`${API_URL}/accounts/signin/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });
  const data = await processResponse(response);
  if (data.access && data.refresh) {
    setAccessToken(data.access);
    setRefreshToken(data.refresh);
  }
  return data;
};

export const refresh = async (token) => {
  const response = await fetch(`${API_URL}/accounts/token/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(token),
  });
  return processResponse(response);
};
