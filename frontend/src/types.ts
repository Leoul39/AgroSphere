export interface RecommendedCrop {
  crop_name: string;
  suitability_score: number;
  rationale: string;
  estimated_growing_days: number;
}

export interface SoilAmendment {
  amendment_type: string;
  application_reason: string;
  recommended_timing: string;
}

export interface RiskFactor {
  risk_type: string;
  description: string;
  mitigation_strategy: string;
}

export interface AgriculturalReport {
  is_farmable: boolean;
  unfarmable_reason: string | null;
  general_location_summary: string;
  coordinate_specific_summary: string;
  climate_summary: string;
  soil_health_summary: string;
  recommended_crops: RecommendedCrop[];
  soil_amendments: SoilAmendment[];
  risk_factors: RiskFactor[];
  irrigation_advice: string;
}
