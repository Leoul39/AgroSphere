export const mockFarmable = {
  "is_farmable": true,
  "unfarmable_reason": null,
  "location_summary": "Located in the Sidama region of Ethiopia, Wondo-Genet is a fertile area known for its diverse agricultural potential. The landscape is characterized by open forest and moderate slopes, providing a stable foundation for small-scale and commercial farming. The region benefits from high-altitude conditions that are ideal for high-value specialty crops.",
  "climate_summary": "Wondo-Genet experiences a temperate highland climate characterized by consistent, moderate temperatures and significant rainfall, particularly during the current Tsedey season. The high humidity levels and frequent rainy days suggest a lush environment suitable for moisture-loving crops. With an elevation of nearly 2000 meters, the area avoids extreme heat, providing a stable growing environment throughout the year.",
  "soil_health_summary": "The soil in Wondo-Genet is a productive clay-loam with a favorable bulk density and deep bedrock, allowing for extensive root penetration. It possesses a moderate cation exchange capacity, indicating a good ability to hold onto nutrients, though phosphorus levels are currently suboptimal. The organic carbon content is healthy, supporting robust microbial activity and soil structure, which is essential for the region's diverse agricultural output.",
  "recommended_crops": [
    {
      "crop_name": "Coffee",
      "suitability_score": 95,
      "rationale": "The high altitude and moderate temperatures of Wondo-Genet are world-renowned for producing high-quality Arabica coffee. The soil's clay-loam texture and organic carbon content provide the necessary nutrients and drainage for healthy coffee development.",
      "estimated_growing_days": 270
    },
    {
      "crop_name": "Enset",
      "suitability_score": 90,
      "rationale": "Enset is a staple crop in the Sidama region, perfectly adapted to the local climate and soil conditions. It is highly resilient and thrives in the deep, nutrient-rich soils found at this elevation.",
      "estimated_growing_days": 365
    },
    {
      "crop_name": "Maize",
      "suitability_score": 85,
      "rationale": "Maize performs exceptionally well in the clay-loam soils of this region, benefiting from the consistent rainfall patterns. It serves as a vital food security crop for the local population.",
      "estimated_growing_days": 120
    }
  ],
  "soil_amendments": [
    {
      "amendment_type": "Phosphorus-rich fertilizer",
      "application_reason": "Phosphorous levels are relatively low (10 ppm), which is a limiting factor for root development and flowering.",
      "recommended_timing": "At planting"
    },
    {
      "amendment_type": "Agricultural Lime",
      "application_reason": "To neutralize the slight acidity and improve the overall nutrient uptake efficiency of the soil.",
      "recommended_timing": "Pre-planting"
    }
  ],
  "risk_factors": [
    {
      "risk_type": "Acidity",
      "description": "The soil pH of 5.9 is slightly acidic, which may limit the availability of certain essential nutrients over time.",
      "mitigation_strategy": "Apply agricultural lime periodically to maintain an optimal pH range for a wider variety of crops."
    },
    {
      "risk_type": "Waterlogging",
      "description": "High clay content and heavy rainfall can lead to waterlogging during peak rainy periods.",
      "mitigation_strategy": "Implement raised bed farming and ensure proper field drainage channels are maintained."
    }
  ],
  "irrigation_advice": "Given the high precipitation and humidity, supplemental irrigation is primarily needed during the drier months to maintain consistent soil moisture. During the current wet season, focus on drainage management to prevent waterlogging in the clay-loam soil. Drip irrigation is recommended for the dry season to maximize water efficiency."
};
