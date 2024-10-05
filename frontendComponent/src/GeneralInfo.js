import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCalendarAlt } from '@fortawesome/free-solid-svg-icons';
import CharacterizationTable from './CharacterizationTable';

const GeneralInfo = ({ startDate, prefix, count, characterization }) => (
  <div className="info-section">
    <div className="selected-date">
      <FontAwesomeIcon icon={faCalendarAlt} size="lg" className="calendar-icon" />
      <span>{startDate.toDateString()}</span>
    </div>
    <p><strong>Prefix:</strong> {prefix}</p>
    <p><strong>Number of Instances:</strong> {count}</p>
    <CharacterizationTable characterization={characterization} />
  </div>
);

export default GeneralInfo;
