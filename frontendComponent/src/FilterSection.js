import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMap, faTable, faSearch } from '@fortawesome/free-solid-svg-icons';
import React, { useState, useEffect } from 'react';

const FilterSection = ({ startDate, setStartDate, handlePreviousDay, handleNextDay, searchTerm, setSearchTerm, view, setView, handleSearch, handleApiResponse }) => {
  
  // Initialize the response state here
  const [response, setResponse] = useState(null);

  const formatDate = (date) => {
    if (!date) return null; // Return null if the date is not provided
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed, so add 1
    const day = String(date.getDate()).padStart(2, '0'); // Add leading zero if necessary
  
    return `${year}-${month}-${day}`;
  };

  const formattedDate = formatDate(startDate);

  const handleSearchClick = () => {
    console.log("Search Term " + searchTerm)
    var apiUrl = "";
    http://localhost:5000/api/ipv6/2023-10-21?prefix=2620:49:4::/48

    if (searchTerm.includes(":")) {
      apiUrl = `http://localhost:5000/api/ipv6/${formattedDate}?prefix=${searchTerm}`;
    }
    else {
      apiUrl = `http://localhost:5000/api/ipv4/${formattedDate}?prefix=${searchTerm}`;
    }
    fetch(apiUrl)
      .then((res) => res.json()) 
      .then((data) => {
        console.log(data); 
        setResponse(data);  
        console.log("DATA "+  response);
        handleApiResponse(data)
      })
      .catch((error) => {
        console.error('Error fetching the API:', error);
      });
    
  };

  return (
    <div className="filter-section">
      <div className="filter-item">
        <label>Select Date:</label>
        <DatePicker
          selected={startDate}
          onChange={(date) => setStartDate(date)}
        />
      </div>
      <div className="filter-item">
        <button onClick={handlePreviousDay}>Previous Day</button>
        <button onClick={handleNextDay}>Next Day</button>
      </div>
      <div className="filter-item search-wrapper">
        <label>Search IP:</label>
        <input
          type="text"
          placeholder="Search by IP"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}  // Update the searchTerm state as the user types
        />
        <button className="search-button" onClick={handleSearchClick}>
          <FontAwesomeIcon icon={faSearch} />
        </button>
      </div>
      <div className="toggle-container">
        <label className={`toggle-switch ${view === "table" ? "on" : ""}`}>
          <input
            type="checkbox"
            checked={view === "table"}
            onChange={() => setView(view === "map" ? "table" : "map")}
          />
          <span className="toggle-slider"></span>
          <FontAwesomeIcon icon={faMap} className="toggle-icon map-icon" />
          <FontAwesomeIcon icon={faTable} className="toggle-icon table-icon" />
        </label>
      </div>
    </div>
  );
};

export default FilterSection;
