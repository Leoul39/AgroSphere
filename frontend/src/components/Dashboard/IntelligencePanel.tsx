import type { AgriculturalReport } from '../../types';
import styles from './IntelligencePanel.module.css';
import { Leaf, MapPin, Droplets, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface Props {
  data: AgriculturalReport | null;
  isLoading: boolean;
  coordinate: { lat: number; lng: number } | null;
}

export default function IntelligencePanel({ data, isLoading, coordinate }: Props) {

  // Idle State
  if (!coordinate && !isLoading && !data) {
    return (
      <div className={styles.idleState}>
        <MapPin size={64} className={styles.idleMapIcon} />
        <h2 className={styles.idleTitle}>Awaiting Coordinates</h2>
        <div className={styles.promptBox}>
          <p>Click anywhere on the satellite map to run an AI-powered agricultural analysis.</p>
        </div>
      </div>
    );
  }

  // Loading State
  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.skeletonHeader} />
        <div className={styles.skeletonGrid}>
          <div className={styles.skeletonCard} />
          <div className={styles.skeletonCard} />
        </div>
        <div className={styles.skeletonPodium} />
        <div className={styles.skeletonGrid}>
          <div className={styles.skeletonCard} />
          <div className={styles.skeletonCard} />
        </div>
      </div>
    );
  }

  if (!data) return null;

  // Unfarmable State
  if (!data.is_farmable) {
    return (
      <div className={styles.reportContainer}>
        <div className={`${styles.statusBadge} ${styles.badgeError}`}>
          <XCircle size={24} />
          <h2>Analysis Complete: Unfarmable Area</h2>
        </div>
        <div className={styles.errorCard}>
          <h3>Why is this area unfarmable?</h3>
          <p>{data.unfarmable_reason}</p>
        </div>
      </div>
    );
  }

  // Success State
  return (
    <div className={styles.reportContainer}>

      {/* Header */}
      <div className={styles.header}>
        <div className={`${styles.statusBadge} ${styles.badgeSuccess}`}>
          <CheckCircle size={24} />
          <h2>High Agricultural Potential</h2>
        </div>
        <div className={styles.locationContainer}>
          <div className={styles.locationSection}>
            <h3 className={styles.locationTitle}>General Region</h3>
            <p className={styles.locationSummary}>{data.general_location_summary}</p>
          </div>
          <div className={styles.locationSection}>
            <h3 className={styles.locationTitle}>Coordinate Terrain (Satellite Verification)</h3>
            <p className={styles.locationSummary}>{data.coordinate_specific_summary}</p>
          </div>
        </div>
      </div>

      {/* Environment Cards */}
      <div className={styles.environmentGrid}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <Leaf className={styles.cardIcon} />
            <h3>Climate</h3>
          </div>
          <p className={styles.cardText}>{data.climate_summary}</p>
        </div>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <MapPin className={styles.cardIcon} />
            <h3>Soil Health</h3>
          </div>
          <p className={styles.cardText}>{data.soil_health_summary}</p>
        </div>
      </div>

      {/* Recommended Crops */}
      <div className={styles.cropsSection}>
        <h3 className={styles.sectionTitle}>Recommended Crops</h3>
        <div className={styles.cropList}>
          {data.recommended_crops.map((crop, idx) => (
            <div key={idx} className={styles.cropItem}>
              <div className={styles.cropHeader}>
                <h4>{crop.crop_name}</h4>
                <span className={styles.scoreBadge}>{crop.suitability_score}% Suitability</span>
              </div>
              <p className={styles.rationale}>{crop.rationale}</p>
              <div className={styles.progressBarBg}>
                <div
                  className={styles.progressBarFill}
                  style={{ width: `${crop.suitability_score}%` }}
                />
              </div>
              <p className={styles.growingDays}>Est. Growing Days: {crop.estimated_growing_days}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Action Plan */}
      <div className={styles.actionGrid}>
        <div className={styles.card}>
          <h3 className={styles.sectionTitle}>Soil Amendments</h3>
          <ul className={styles.list}>
            {data.soil_amendments.map((amendment, idx) => (
              <li key={idx} className={styles.listItem}>
                <strong>{amendment.amendment_type}</strong>
                <span>{amendment.recommended_timing}</span>
                <p>{amendment.application_reason}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.card}>
          <h3 className={styles.sectionTitle}>Risk Factors</h3>
          <ul className={styles.list}>
            {data.risk_factors.map((risk, idx) => (
              <li key={idx} className={styles.listItem}>
                <strong>{risk.risk_type} <AlertTriangle size={14} className={styles.warningIcon} /></strong>
                <p>{risk.description}</p>
                <div className={styles.mitigation}>
                  <em>Mitigation:</em> {risk.mitigation_strategy}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Irrigation */}
      <div className={styles.irrigationCard}>
        <div className={styles.cardHeader}>
          <Droplets className={styles.cardIcon} />
          <h3>Irrigation Advice</h3>
        </div>
        <p>{data.irrigation_advice}</p>
      </div>

    </div>
  );
}
