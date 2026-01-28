import { create } from 'zustand';

interface SelectionState {
    selectedEntityId: string | null;
    topologyAnchorId: string | null;
    history: string[];
    topologyHistory: string[];
    setSelectedEntityId: (id: string | null) => void;
    pushSelection: (id: string) => void;
    popSelection: () => void;
    setTopologyAnchorId: (id: string | null) => void;
    jumpToHistoryStep: (index: number) => void;
    resetTopologyAnchor: () => void;
}

export const useSelectionStore = create<SelectionState>((set) => ({
    selectedEntityId: null,
    topologyAnchorId: null,
    history: [],
    topologyHistory: [],
    setSelectedEntityId: (id) =>
        set({
            selectedEntityId: id,
            topologyAnchorId: id,
            history: id ? [id] : [],
            topologyHistory: id ? [id] : [],
        }),
    pushSelection: (id) =>
        set((state) => ({
            selectedEntityId: id,
            topologyAnchorId: id,
            history: [...state.history, id],
            topologyHistory: [...state.topologyHistory, id],
        })),
    popSelection: () =>
        set((state) => {
            const newHistory = [...state.history];
            newHistory.pop();
            const newTopoHistory = [...state.topologyHistory];
            newTopoHistory.pop();
            const prevId = newHistory[newHistory.length - 1] || null;
            return {
                selectedEntityId: prevId,
                topologyAnchorId: prevId,
                history: newHistory,
                topologyHistory: newTopoHistory,
            };
        }),
    setTopologyAnchorId: (id) =>
        set((state) => ({
            topologyAnchorId: id,
            topologyHistory: id ? [...state.topologyHistory, id] : state.topologyHistory,
        })),
    jumpToHistoryStep: (index) =>
        set((state) => {
            const newHistory = state.topologyHistory.slice(0, index + 1);
            const anchorId = newHistory[newHistory.length - 1] || null;
            return {
                topologyAnchorId: anchorId,
                topologyHistory: newHistory,
            };
        }),
    resetTopologyAnchor: () =>
        set((state) => ({
            topologyAnchorId: state.selectedEntityId,
            topologyHistory: state.selectedEntityId ? [state.selectedEntityId] : [],
        })),
}));
