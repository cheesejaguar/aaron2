import { create } from "zustand";

interface UIState {
  sidebarCollapsed: boolean;
  coachPanelOpen: boolean;
  toggleSidebar: () => void;
  toggleCoachPanel: () => void;
  setCoachPanelOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()((set) => ({
  sidebarCollapsed: false,
  coachPanelOpen: false,
  toggleSidebar: () =>
    set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  toggleCoachPanel: () =>
    set((s) => ({ coachPanelOpen: !s.coachPanelOpen })),
  setCoachPanelOpen: (open) => set({ coachPanelOpen: open }),
}));
