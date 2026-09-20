import { MapContainer, TileLayer, Marker, useMapEvents, useMap, GeoJSON, Polygon, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';
import styles from './MapExplorer.module.css';
import africaBorders from './africa.json';
import ethiopiaRegions from './ethiopia-regions.json';
import ethiopiaCities from './ethiopia-cities.json';

// Fix Leaflet's default icon path issues in React
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

interface MapExplorerProps {
  selectedCoordinate: { lat: number; lng: number } | null;
  onMapClick: (lat: number, lng: number) => void;
}

// Helper hook to dynamically apply CSS classes based on zoom level
function ZoomHandler() {
  const map = useMap();
  useEffect(() => {
    const updateZoomClass = () => {
      const z = map.getZoom();
      const container = map.getContainer();

      // Clear previous classes
      container.className = container.className.replace(/\bzoom-level-\d+\b/g, '');

      // Apply new dynamic class (6-tier system)
      if (z <= 3) container.classList.add('zoom-level-1'); // Africa wide
      else if (z === 4) container.classList.add('zoom-level-2'); // Africa near
      else if (z === 5) container.classList.add('zoom-level-3'); // Ethiopia wide
      else if (z === 6) container.classList.add('zoom-level-4'); // Ethiopia near (Cities visible but small)
      else if (z <= 8) container.classList.add('zoom-level-5'); // Local (Cities full size)
      else container.classList.add('zoom-level-6'); // Farm (Hide cities and text)
    };

    map.on('zoom', updateZoomClass);
    updateZoomClass(); // init

    return () => {
      map.off('zoom', updateZoomClass);
    };
  }, [map]);
  return null;
}

// Helper hook to capture map clicks
function ClickCapturer({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// Helper hook to fly map to selected coordinate
function MapFlyTo({ coordinate }: { coordinate: { lat: number; lng: number } | null }) {
  const map = useMap();
  useEffect(() => {
    if (coordinate) {
      // Zoom in to level 12 if zoomed out, otherwise keep current zoom
      const targetZoom = Math.max(map.getZoom(), 12);
      map.flyTo([coordinate.lat, coordinate.lng], targetZoom, {
        duration: 1.5,
      });
    }
  }, [coordinate, map]);
  return null;
}

export default function MapExplorer({ selectedCoordinate, onMapClick }: MapExplorerProps) {
  // Center of Africa as default
  const defaultCenter: [number, number] = [8.9806, 38.7578]; // Addis Ababa
  const defaultZoom = 4; // Zoomed out slightly to see more of Africa

  // Calculate a small bounding box (~50m) around the point to simulate the "analyzed land"
  const offset = 0.00005;
  const polygonPositions: [number, number][] | null = selectedCoordinate
    ? [
      [selectedCoordinate.lat + offset, selectedCoordinate.lng - offset],
      [selectedCoordinate.lat + offset, selectedCoordinate.lng + offset],
      [selectedCoordinate.lat - offset, selectedCoordinate.lng + offset],
      [selectedCoordinate.lat - offset, selectedCoordinate.lng - offset],
    ]
    : null;

  const onEachCountry = (feature: any, layer: L.Layer) => {
    if (feature.properties && feature.properties.name) {
      layer.bindTooltip(feature.properties.name, {
        permanent: true,
        direction: 'center',
        className: 'countryLabel'
      });
    }
  };

  const onEachRegion = (feature: any, layer: L.Layer) => {
    const name = feature.properties?.shapeName; // geoBoundaries uses shapeName

    // Hide labels for tiny city-state regions because they clutter the map 
    // and are already represented by our City Markers! Also hide crescent regions like Benishangul-Gumuz.
    const hiddenRegions = [
      'Addis Ababa', 'Dire Dawa', 'Harari Region',
      'Benshangul-Gumaz', 'Benishangul Gumuz', 'Benishangul-Gumuz', 'Benshangul Gumuz'
    ];

    if (name && !hiddenRegions.includes(name)) {
      layer.bindTooltip(name, {
        permanent: true,
        direction: 'center',
        className: 'regionLabel'
      });
    }
  };

  return (
    <div className={styles.mapContainer}>
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%', borderRadius: '12px' }}
      >
        {/* Google Maps Satellite */}
        <TileLayer
          url="http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
          attribution='&copy; <a href="https://www.google.com/maps">Google Maps</a>'
          maxZoom={20}
        />

        {/* Africa Borders GeoJSON */}
        <GeoJSON
          data={africaBorders as any}
          onEachFeature={onEachCountry}
          style={{
            color: 'rgba(255, 255, 255, 0.4)',
            weight: 1.5,
            fillOpacity: 0,
            dashArray: '5 5'
          }}
        />

        {/* Ethiopia Regions GeoJSON */}
        <GeoJSON
          data={ethiopiaRegions as any}
          onEachFeature={onEachRegion}
          style={{
            color: '#a8ffb2',
            weight: 1.5,
            fillOpacity: 0,
            opacity: 0.6,
            dashArray: '3 3'
          }}
        />

        {/* Ethiopia Major Cities */}
        {ethiopiaCities.map((city, idx) => (
          <CircleMarker
            key={idx}
            center={[city.lat, city.lng]}
            radius={4}
            pathOptions={{ color: '#ffffff', fillColor: '#00ff00', fillOpacity: 0.8, className: 'city-marker' }}
          >
            <Tooltip permanent direction="bottom" className="cityLabel" offset={[0, 5]}>
              {city.name}
            </Tooltip>
          </CircleMarker>
        ))}

        <ZoomHandler />
        <ClickCapturer onMapClick={onMapClick} />
        <MapFlyTo coordinate={selectedCoordinate} />

        {selectedCoordinate && (
          <>
            <Marker position={[selectedCoordinate.lat, selectedCoordinate.lng]} />
            {polygonPositions && (
              <Polygon
                positions={polygonPositions}
                pathOptions={{ color: 'var(--sphere-light-green)', fillColor: 'var(--sphere-green)', fillOpacity: 0.4, weight: 2 }}
              />
            )}
          </>
        )}
      </MapContainer>
    </div>
  );
}
