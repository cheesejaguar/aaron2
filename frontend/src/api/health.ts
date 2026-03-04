import api from "./client";
import type {
  BPLog, BPLogCreate, WeightLog, WeightLogCreate,
  CholesterolLog, CholesterolLogCreate, DashboardData,
} from "@/types";

export const healthApi = {
  listBP: (limit = 30) =>
    api.get<BPLog[]>("/health/blood-pressure", { params: { limit } }).then((r) => r.data),

  createBP: (data: BPLogCreate) =>
    api.post<BPLog>("/health/blood-pressure", data).then((r) => r.data),

  listWeight: (limit = 30) =>
    api.get<WeightLog[]>("/health/weight", { params: { limit } }).then((r) => r.data),

  createWeight: (data: WeightLogCreate) =>
    api.post<WeightLog>("/health/weight", data).then((r) => r.data),

  listCholesterol: (limit = 30) =>
    api.get<CholesterolLog[]>("/health/cholesterol", { params: { limit } }).then((r) => r.data),

  createCholesterol: (data: CholesterolLogCreate) =>
    api.post<CholesterolLog>("/health/cholesterol", data).then((r) => r.data),

  dashboard: () =>
    api.get<DashboardData>("/health/dashboard").then((r) => r.data),
};
