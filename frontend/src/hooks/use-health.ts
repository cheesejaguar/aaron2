import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { healthApi } from "@/api/health";
import type { BPLogCreate, WeightLogCreate, CholesterolLogCreate } from "@/types";

export function useDashboard() {
  return useQuery({
    queryKey: ["health", "dashboard"],
    queryFn: healthApi.dashboard,
  });
}

export function useBPLogs(limit = 30) {
  return useQuery({
    queryKey: ["health", "bp", limit],
    queryFn: () => healthApi.listBP(limit),
  });
}

export function useCreateBPLog() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BPLogCreate) => healthApi.createBP(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["health"] });
      toast.success("Blood pressure logged");
    },
  });
}

export function useWeightLogs(limit = 30) {
  return useQuery({
    queryKey: ["health", "weight", limit],
    queryFn: () => healthApi.listWeight(limit),
  });
}

export function useCreateWeightLog() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WeightLogCreate) => healthApi.createWeight(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["health"] });
      toast.success("Weight logged");
    },
  });
}

export function useCholesterolLogs(limit = 10) {
  return useQuery({
    queryKey: ["health", "cholesterol", limit],
    queryFn: () => healthApi.listCholesterol(limit),
  });
}

export function useCreateCholesterolLog() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CholesterolLogCreate) => healthApi.createCholesterol(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["health"] });
      toast.success("Cholesterol logged");
    },
  });
}
