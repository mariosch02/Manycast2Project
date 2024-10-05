import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import "leaflet/dist/leaflet.css";
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const customMarker = new L.Icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const MapView = ({ instances }) => (
  <div className="map-section">
    <MapContainer
      minZoom={2.4}
      center={[15, 0]}
      zoom={2}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      {instances.map((site) => (
        <Marker key={site.id} position={site.position} icon={customMarker}>
          <Popup>
            <div>
              <strong>{site.city}</strong> ({site.code_country})
              <br />
              ID: {site.id}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  </div>
);

export default MapView;
