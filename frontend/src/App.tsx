import { useState } from 'react';
import styles from './App.module.css';
import type { AgriculturalReport } from './types';
import MapExplorer from './components/Map/MapExplorer';
import IntelligencePanel from './components/Dashboard/IntelligencePanel';

const logoUrl = '/agrosphere-logo-transparent.svg';

function App() {
  const [selectedCoordinate, setSelectedCoordinate] = useState<{ lat: number; lng: number } | null>(null);
  const [analysisData, setAnalysisData] = useState<AgriculturalReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const [latInput, setLatInput] = useState('');
  const [lngInput, setLngInput] = useState('');

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const lat = parseFloat(latInput);
    const lng = parseFloat(lngInput);
    if (!isNaN(lat) && !isNaN(lng)) {
      handleMapClick(lat, lng);
    }
  };

  const handleMapClick = async (lat: number, lng: number) => {
    setSelectedCoordinate({ lat, lng });
    setIsLoading(true);
    setAnalysisData(null);

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_BASE_URL}/api/v1/analyses/summary?lat=${lat}&lon=${lng}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to fetch analysis.");
      }

      setAnalysisData(data);
    } catch (err: any) {
      console.error(err);
      // Render an error state within the Intelligence Panel
      setAnalysisData({
        is_farmable: false,
        unfarmable_reason: `System Error: ${err.message}. Ensure the Python backend is running properly.`,
        general_location_summary: "",
        coordinate_specific_summary: "",
        climate_summary: "",
        soil_health_summary: "",
        irrigation_advice: "",
        recommended_crops: [],
        soil_amendments: [],
        risk_factors: []
      } as AgriculturalReport);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.appContainer}>

      {/* Fixed Left Sidebar */}
      <div className={styles.sidebar}>

        {/* Branding */}
        <div className={styles.brandHeader}>
          <img src={logoUrl} alt="AgroSphere Logo" className={styles.logo} />
          <div className={styles.brandTextContainer}>
            <h1 className={styles.brandTitle}>
              <span className={styles.textMain}>Agro</span>
              <span className={styles.textGreen}>Sphere</span>
            </h1>
            <p className={styles.tagline}>Data. Insights. Smarter Farming.</p>
          </div>
        </div>

        {/* Map Card */}
        <div className={styles.mapCard}>
          <MapExplorer
            selectedCoordinate={selectedCoordinate}
            onMapClick={handleMapClick}
          />
        </div>

        {/* Map Hint Text */}
        {!selectedCoordinate && (
          <p className={styles.mapHintText}>
            Click anywhere on the Ethiopia map to analyze agricultural potential.
          </p>
        )}

        {/* Coordinates Widget & Manual Input */}
        <div className={styles.coordinateWidget}>
          {selectedCoordinate ? (
            <div className={styles.coordinateData}>
              <strong>Target Acquired:</strong>
              <p>Lat: {selectedCoordinate.lat.toFixed(4)}, Lng: {selectedCoordinate.lng.toFixed(4)}</p>
            </div>
          ) : (
            <div className={styles.coordinateData}>
              <strong>Awaiting Target...</strong>
              <p>Click map or enter manually</p>
            </div>
          )}

          <form
            className={styles.coordForm}
            onSubmit={handleManualSubmit}
          >
            <div className={styles.coordInputsWrapper}>
              <div className={styles.inputGroup}>
                <label>LAT</label>
                <input
                  type="number"
                  step="any"
                  value={latInput}
                  onChange={(e) => setLatInput(e.target.value)}
                  placeholder="e.g. 9.03"
                  className={styles.coordInput}
                />
              </div>
              <div className={styles.inputDivider}></div>
              <div className={styles.inputGroup}>
                <label>LNG</label>
                <input
                  type="number"
                  step="any"
                  value={lngInput}
                  onChange={(e) => setLngInput(e.target.value)}
                  placeholder="e.g. 38.74"
                  className={styles.coordInput}
                />
              </div>
            </div>
            <button type="submit" className={styles.coordSubmitBtn}>
              Analyze
            </button>
          </form>
        </div>
      </div>

      {/* Scrollable Main Content Area */}
      <div className={styles.mainContent}>
        <IntelligencePanel
          data={analysisData}
          isLoading={isLoading}
          coordinate={selectedCoordinate}
        />
      </div>

    </div>
  );
}

export default App;
