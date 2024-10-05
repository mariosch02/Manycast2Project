import React from 'react';

const CharacterizationTable = ({ characterization }) => {
  const rows = [
    { protocol: 'MAnycast ICMPv6', data: characterization.MAnycastICMPv6 },
    { protocol: 'MAnycast TCPv6', data: characterization.MAnycastTCPv6 },
    { protocol: 'MAnycast UDPv6', data: characterization.MAnycastUDPv6 },
    { protocol: 'iGreedy ICMPv6', data: characterization.iGreedyICMPv6 },
    { protocol: 'iGreedy TCPv6', data: characterization.iGreedyTCPv6 }
  ];

  return (
    <table className="characterization-table">
      <thead>
        <tr>
          <th>Protocol</th>
          <th>Anycast</th>
          <th>Instances</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={index}>
            <td>{row.protocol}</td>
            <td>{row.data.anycast ? 'Yes' : 'No'}</td>
            <td>{row.data.instances}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default CharacterizationTable;
