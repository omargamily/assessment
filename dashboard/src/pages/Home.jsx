import DashboardContent from "../components/DashboardContent";

const HomePage = () => {
  return (
    <div className="container mx-auto p-4">
      <DashboardContent title="Overview">
        <p className="text-text-secondary">Welcome to your dashboard!</p>
      </DashboardContent>
    </div>
  );
};

export default HomePage;
