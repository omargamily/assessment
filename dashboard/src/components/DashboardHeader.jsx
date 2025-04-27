const DashboardHeader = () => {
  return (
    <div className="flex justify-between items-center mb-6">
      <h1 className="text-2xl font-semibold text-text-primary">Dashboard</h1>
      <button className="bg-button-primary-bg hover:bg-button-primary-hover-bg text-button-text-on-blue font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline">
        Create Plan
      </button>
    </div>
  );
};

export default DashboardHeader;
