import React, { useState } from "react";
import FilterSection from './FilterSection';
import MapView from './MapView';
import TableView from './TableView';
import GeneralInfo from './GeneralInfo';
import "./App.css";

// useEffect(() => {
//   fetch('http://localhost:5000/api/data')
//       .then(response => response.text()) 
//       .then(text => setData(text))
//       .catch(error => console.error('Error fetching data:', error));
// }, []);



const anycastSites = {
  prefix: "2001:1218:600d::/48",
  count: 3,
  characterization: {
    MAnycastICMPv6: { anycast: true, instances: 2 },
    MAnycastTCPv6: { anycast: true, instances: 2 },
    MAnycastUDPv6: { anycast: null, instances: 0 },
    iGreedyICMPv6: { anycast: false, instances: 1 },
    iGreedyTCPv6: { anycast: false, instances: 1 },
  },
  instances: [
    { city: "Paris", code_country: "FR", id: "LBG", position: [48.8566, 2.3522] },
    { city: "New York", code_country: "US", id: "NYC", position: [40.7128, -74.0060] },
    { city: "Tokyo", code_country: "JP", id: "TYO", position: [35.6895, 139.6917] }
  ]
};

const App = () => {
  const [startDate, setStartDate] = useState(new Date());
  const [searchTerm, setSearchTerm] = useState("");
  const [view, setView] = useState("map");
  const [anycastInstances, setAnycastInstances] = useState([])

  const handleNextDay = () => {
    const nextDay = new Date(startDate);
    nextDay.setDate(startDate.getDate() + 1);
    setStartDate(nextDay);
  };

  const handlePreviousDay = () => {
    const previousDay = new Date(startDate);
    previousDay.setDate(startDate.getDate() - 1);
    setStartDate(previousDay);
  };

  // const handleSearch = () => {
  //   setStartDate
  //   setSearchTerm
  // }

  return (
    <div className="container">
      <FilterSection
        startDate={startDate}
        setStartDate={setStartDate}
        handlePreviousDay={handlePreviousDay}
        handleNextDay={handleNextDay}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        view={view}
        setView={setView}
      />
      <div className="content">
        {view === "map" ? <MapView instances={anycastSites.instances} /> : <TableView instances={anycastSites.instances} />}
        <GeneralInfo startDate={startDate} prefix={anycastSites.prefix} count={anycastSites.count} characterization={anycastSites.characterization} />
      </div>
    </div>
  );
};

export default App;
