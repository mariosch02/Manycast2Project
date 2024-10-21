import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import FilterSection from "./FilterSection";
import MapView from "./MapView";
import TableView from "./TableView";
import GeneralInfo from "./GeneralInfo";
import "./App.css";

const App = () => {
  const [searchParams] = useSearchParams();
  const initialDate = searchParams.get("date") || new Date().toISOString().split("T")[0];
  const initialPrefix = searchParams.get("prefix") || "";
  const [startDate, setStartDate] = useState(new Date(initialDate));
  const [searchTerm, setSearchTerm] = useState(initialPrefix);
  const [view, setView] = useState("map");
  const [dataResponse, setDataResponse] = useState(null);
  const [anycastSites, setAnycastSites] = useState({
    prefix: "",
    count: 0,
    characterization: {},
    instances: [],
  });

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

  useEffect(() => {
    var newAnycastSites = null
    if (dataResponse && dataResponse.length > 0) {
        // if IP is ipv6

        if (dataResponse[0].Prefix.includes(":")) {
          newAnycastSites = {
            prefix: dataResponse[0].Prefix,
            count: dataResponse[0].Count,
            characterization: {
              MAnycastICMPv6: { anycast: dataResponse[0].MAnycast_ICMPv6, instances: dataResponse[0].MAnycast_ICMPv6_Count },
              MAnycastTCPv6: { anycast: dataResponse[0].MAnycast_TCPv6, instances: dataResponse[0].MAnycast_TCPv6_Count },
              MAnycastUDPv6: { anycast: dataResponse[0].MAnycast_UDPv6, instances: dataResponse[0].MAnycast_UDPv6_Count },
              iGreedyICMPv6: { anycast: dataResponse[0].iGreedyICMPv6, instances: dataResponse[0].iGreedyICMPv6_Count },
              iGreedyTCPv6: { anycast: dataResponse[0].iGreedyTCPv6, instances: dataResponse[0].iGreedyTCPv6_Count },
            },
            instances: dataResponse.map((item) => ({
              city: item.City,
              code_country: item.CodeCountry,
              id: item.Id,
              position: [item.Latitude, item.Longitude],
            })),
          };
      }
      // if IP is ipv4
        else {
          console.log("mpenw dame?")
          newAnycastSites = {
            prefix: dataResponse[0].Prefix,
            count: dataResponse[0].Count,
            characterization: {
              MAnycastICMPv4: { anycast: dataResponse[0].MAnycast_ICMPv4, instances: dataResponse[0].MAnycast_ICMPv4_Count },
              MAnycastTCPv4: { anycast: dataResponse[0].MAnycast_TCPv4, instances: dataResponse[0].MAnycast_TCPv4_Count },
              MAnycastUDPv4: { anycast: dataResponse[0].MAnycast_UDPv4, instances: dataResponse[0].MAnycast_UDPv4_Count },
              iGreedyICMPv4: { anycast: dataResponse[0].iGreedyICMPv4, instances: dataResponse[0].iGreedyICMPv4_Count },
              iGreedyTCPv4: { anycast: dataResponse[0].iGreedyTCPv4, instances: dataResponse[0].iGreedyTCPv4_Count },
            },
            instances: dataResponse.map((item) => ({
              city: item.City,
              code_country: item.CodeCountry,
              id: item.Id,
              position: [item.Latitude, item.Longitude],
            })),
          };
      }
      setAnycastSites(newAnycastSites);
    }
  }, [dataResponse]);

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
        handleApiResponse={setDataResponse}
      />
      <div className="content">
        {view === "map" ? (
          <MapView instances={anycastSites.instances} />
        ) : (
          <TableView instances={anycastSites.instances} />
        )}
        <GeneralInfo
          startDate={startDate}
          prefix={anycastSites.prefix}
          count={anycastSites.count}
          characterization={anycastSites.characterization}
        />
      </div>
    </div>
  );
};

export default App;