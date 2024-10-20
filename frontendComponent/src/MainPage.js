import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { useNavigate } from "react-router-dom";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const MainPage = () => {
  const [date, setDate] = useState(new Date().toLocaleDateString());
  const [chartData, setChartData] = useState({ labels: [], datasets: [] });
  const [statistics, setStatistics] = useState({});
  const [selectedProtocols, setSelectedProtocols] = useState({});
  const [dateRange, setDateRange] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const generateRandomStats = (startDate, endDate, maxDaysIncrement) => {
      const protocols = [
        "MAnycastICMPv4", "MAnycastTCPv4", "MAnycastUDPv4", 
        "iGreedyICMPv4", "iGreedyTCPv4", "MAnycastICMPv6", 
        "MAnycastTCPv6", "MAnycastUDPv6", "iGreedyICMPv6", 
        "iGreedyTCPv6"
      ];

      let stats = {};
      let currentDate = new Date(startDate);

      while (currentDate <= new Date(endDate)) {
        const dateKey = currentDate.toISOString().split('T')[0];
        stats[dateKey] = {};

        protocols.forEach(protocol => {
          stats[dateKey][protocol] = Math.floor(Math.random() * (50000 - 100 + 1)) + 100;
        });

        const daysIncrement = Math.floor(Math.random() * maxDaysIncrement) + 1;
        currentDate.setDate(currentDate.getDate() + daysIncrement);
      }

      return stats;
    };

    const startDate = "2022-09-01";
    const endDate = "2024-11-01";
    const maxDaysIncrement = 1;
    
    setStatistics(generateRandomStats(startDate, endDate, maxDaysIncrement));
  }, []);

  const protocolColors = {
    "MAnycastICMPv4": "#4B8BAE",
    "MAnycastTCPv4":  "#E07B39",
    "MAnycastUDPv4": "#A43BB0",
    "iGreedyICMPv4": "#1C8731",
    "iGreedyTCPv4":  "#D97A7A",
    "MAnycastICMPv6": "#A09E6E",
    "MAnycastTCPv6": "#30D5C8",
    "MAnycastUDPv6": "#9A3334",
    "iGreedyICMPv6": "#F1C40F",
    "iGreedyTCPv6": "#3498DB",
  };

  const lastDate = Object.keys(statistics).length > 0 ? Object.keys(statistics).slice(-1)[0] : null;

  useEffect(() => {
    const initialSelection = Object.keys(protocolColors).reduce((acc, protocol) => {
      acc[protocol] = false;
      return acc;
    }, {});
    setSelectedProtocols(initialSelection);
  }, []);

  const filterDates = (range) => {
    const now = new Date();
    const dateLabels = Object.keys(statistics);

    switch (range) {
      case "7days":
        return dateLabels.filter(date => (now - new Date(date)) / (1000 * 60 * 60 * 24) <= 7);
      case "month":
        return dateLabels.filter(date => (now - new Date(date)) / (1000 * 60 * 60 * 24) <= 30);
      case "year":
        return dateLabels.filter(date => (now - new Date(date)) / (1000 * 60 * 60 * 24) <= 365);
      default:
        return dateLabels;
    }
  };

  useEffect(() => {
    if (Object.keys(statistics).length === 0) return;

    const labels = filterDates(dateRange);

    const datasets = Object.keys(protocolColors)
      .filter(protocol => selectedProtocols[protocol])
      .map(protocol => ({
        label: protocol,
        data: labels.map(date => statistics[date]?.[protocol] || 0),
        borderColor: protocolColors[protocol],
        backgroundColor: `${protocolColors[protocol]}80`,
        fill: false,
        pointRadius: 0,
        tension: 0.4,
      }));

    setChartData({
      labels: labels.map(date => new Date(date).toLocaleDateString()),
      datasets: datasets,
    });
  }, [selectedProtocols, dateRange, statistics]);

  const handleProtocolChange = (protocol) => {
    setSelectedProtocols(prevState => ({
      ...prevState,
      [protocol]: !prevState[protocol]
    }));
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = () => {
    if (searchQuery.trim() && lastDate) {
      navigate(`/app?date=${lastDate}&prefix=${searchQuery}`);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearchSubmit();
    }
  };

  const styles = {
    container: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      fontFamily: "Arial, sans-serif",
      color: "#333",
      padding: "20px",
      maxWidth: "100%",
      margin: "auto",
      backgroundColor: "#f0f4f8",
    },
    title: {
      color: "#4B8BAE",
      fontSize: "1.5rem",
      marginBottom: "15px",
    },
    sectionTitle: {
      fontSize: "1.2rem",
      color: "#4B8BAE",
      marginBottom: "8px",
    },
    table: {
      width: "75%",
      borderCollapse: "collapse",
      marginBottom: "25px",
    },
    th: {
      backgroundColor: "#4B8BAE",
      color: "#fff",
      padding: "8px",
      fontWeight: "bold",
      border: "1px solid #ddd",
    },
    td: {
      padding: "6px",
      textAlign: "center",
      border: "1px solid #ddd",
      backgroundColor: "#f9f9f9",
    },
    chartLegendContainer: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      marginBottom: "25px",
      backgroundColor: "#ffffff",
      padding: "20px",
      borderRadius: "8px",
      boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
      width: "75%",
    },
    legend: {
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gap: "10px",
      marginTop: "15px",
    },
    legendItem: {
      display: "flex",
      alignItems: "center",
      padding: "4px 8px",
      borderRadius: "5px",
    },
    colorBox: (color) => ({
      width: "10px",
      height: "10px",
      backgroundColor: color,
      marginRight: "5px",
      borderRadius: "50%",
    }),
    searchContainer: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "#e9f5fc",
      padding: "30px",
      borderRadius: "12px",
      boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
      marginTop: "25px",
      width: "80%",
    },
    searchTitle: {
      fontSize: "1.4rem",
      color: "#2c3e50",
      marginBottom: "20px",
      fontWeight: "bold",
    },
    searchInputContainer: {
      display: "flex",
      alignItems: "center",
      width: "100%",
      maxWidth: "600px",
    },
    searchInput: {
      padding: "12px",
      fontSize: "1rem",
      width: "100%",
      borderTopLeftRadius: "8px",
      borderBottomLeftRadius: "8px",
      border: "1px solid #ddd",
      boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
    },
    searchButton: {
      padding: "12px",
      backgroundColor: "#3498db",
      borderTopRightRadius: "8px",
      borderBottomRightRadius: "8px",
      border: "none",
      cursor: "pointer",
      color: "#fff",
      fontWeight: "bold",
    },
    dateRangeContainer: {
      display: "flex",
      justifyContent: "center",
      gap: "10px",
      marginTop: "10px",
    },
    dateRangeButton: {
      padding: "8px 10px",
      borderRadius: "5px",
      border: "1px solid #ddd",
      backgroundColor: "#e9ecef",
      cursor: "pointer",
      fontWeight: "bold",
      color: "#333",
      transition: "background-color 0.3s, color 0.3s",
    },
    dateRangeButtonActive: {
      backgroundColor: "#4B8BAE",
      color: "#fff",
    },
    searchIcon: {
      width: "16px",
      height: "16px",
      verticalAlign: "middle",
    },
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Network Stats for {date}</h2>

      {/* Statistics Table */}
      <h3 style={styles.sectionTitle}>Statistics for {lastDate}</h3>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Metric</th>
            <th style={styles.th}>Count</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(statistics).length > 0 
            ? Object.entries(statistics[Object.keys(statistics)[0]]).map(([protocol, count]) => (
              <tr key={protocol}>
                <td style={styles.td}>{protocol}</td>
                <td style={styles.td}>{count}</td>
              </tr>
            ))
            : <tr><td colSpan="2">No data available</td></tr>}
        </tbody>
      </table>

      {/* Chart and Legend */}
      <div style={styles.chartLegendContainer}>
        <h3 style={styles.sectionTitle}>Instances Over Time</h3>
        <div style={{ width: "100%" }}>
          <Line
            data={chartData}
            options={{
              responsive: true,
              plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
                title: { display: true, text: "Instance Count Over Time" },
              },
              scales: {
                x: { title: { display: true, text: "Date" } },
                y: { title: { display: true, text: "Instance Count" } },
              },
            }}
          />
        </div>
        <div style={styles.legend}>
          {Object.keys(protocolColors).map(protocol => (
            <div key={protocol} style={styles.legendItem}>
              <input
                type="checkbox"
                checked={selectedProtocols[protocol]}
                onChange={() => handleProtocolChange(protocol)}
              />
              <div style={styles.colorBox(protocolColors[protocol])}></div>
              <label>{protocol}</label>
            </div>
          ))}
        </div>

        {/* Date Range Buttons */}
        <div style={styles.dateRangeContainer}>
          {["7days", "month", "year", "all"].map(range => (
            <button
              key={range}
              onClick={() => handleDateRangeChange(range)}
              style={{
                ...styles.dateRangeButton,
                ...(dateRange === range ? styles.dateRangeButtonActive : {})
              }}
            >
              {range === "7days" ? "Last 7 Days" : range === "month" ? "Last Month" : range === "year" ? "Last Year" : "All Time"}
            </button>
          ))}
        </div>
      </div>

      {/* Search Section */}
      <div style={styles.searchContainer}>
        <h3 style={styles.searchTitle}>Search for a Particular Prefix</h3>
        <div style={styles.searchInputContainer}>
          <input
            type="text"
            placeholder="Enter protocol prefix..."
            style={styles.searchInput}
            value={searchQuery}
            onChange={handleSearchChange}
            onKeyDown={handleKeyDown}
          />
          <button onClick={handleSearchSubmit} style={styles.searchButton}>
            <svg style={styles.searchIcon} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M10 2a8 8 0 105.293 13.707l5.707 5.707a1 1 0 101.414-1.414l-5.707-5.707A8 8 0 0010 2zm0 2a6 6 0 110 12 6 6 0 010-12z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MainPage;
