import { describe, it, expect, beforeEach } from "vitest";
import { useUIStore } from "./ui-store";

describe("useUIStore", () => {
  beforeEach(() => {
    useUIStore.setState({
      sidebarCollapsed: false,
      coachPanelOpen: false,
    });
  });

  it("starts with sidebar expanded and coach panel closed", () => {
    const state = useUIStore.getState();
    expect(state.sidebarCollapsed).toBe(false);
    expect(state.coachPanelOpen).toBe(false);
  });

  it("toggles sidebar", () => {
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarCollapsed).toBe(true);

    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarCollapsed).toBe(false);
  });

  it("toggles coach panel", () => {
    useUIStore.getState().toggleCoachPanel();
    expect(useUIStore.getState().coachPanelOpen).toBe(true);

    useUIStore.getState().toggleCoachPanel();
    expect(useUIStore.getState().coachPanelOpen).toBe(false);
  });

  it("sets coach panel open directly", () => {
    useUIStore.getState().setCoachPanelOpen(true);
    expect(useUIStore.getState().coachPanelOpen).toBe(true);

    useUIStore.getState().setCoachPanelOpen(false);
    expect(useUIStore.getState().coachPanelOpen).toBe(false);
  });
});
