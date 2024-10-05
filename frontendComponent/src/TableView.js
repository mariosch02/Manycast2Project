import React from 'react';

const TableView = ({ instances }) => (
  <div className="table-section">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>City</th>
          <th>Country Code</th>
          <th>ID</th>
          <th>Latitude</th>
          <th>Longitude</th>
        </tr>
      </thead>
      <tbody>
        {instances.map((instance, index) => (
          <tr key={index}>
            <td>{index + 1}</td>
            <td>{instance.city}</td>
            <td>{instance.code_country}</td>
            <td>{instance.id}</td>
            <td>{instance.position[0]}</td>
            <td>{instance.position[1]}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default TableView;
