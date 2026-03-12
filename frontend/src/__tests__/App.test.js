import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App, { AppRoutes } from "../App";

const ROUTER_FUTURE_FLAGS = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
};

// Mock the page components
jest.mock("../pages/HomePage", () => {
  return function MockHomePage() {
    return <div>HomePage</div>;
  };
});

jest.mock("../pages/SessionPage", () => {
  return function MockSessionPage() {
    return <div>SessionPage</div>;
  };
});

describe("App", () => {
  it("should render App component", () => {
    render(<App />);

    expect(screen.getByText("HomePage")).toBeInTheDocument();
  });

  it("should render HomePage at root route", () => {
    render(
      <MemoryRouter initialEntries={["/"]} future={ROUTER_FUTURE_FLAGS}>
        <AppRoutes />
      </MemoryRouter>,
    );

    expect(screen.getByText("HomePage")).toBeInTheDocument();
  });

  it("should render SessionPage at session route", () => {
    render(
      <MemoryRouter
        initialEntries={["/session/TEST1234"]}
        future={ROUTER_FUTURE_FLAGS}
      >
        <AppRoutes />
      </MemoryRouter>,
    );

    expect(screen.getByText("SessionPage")).toBeInTheDocument();
  });
});
