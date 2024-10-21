import React from 'react';

const CharacterizationTable = ({ characterization }) => {

  const hasV4Key = Object.keys(characterization).some(key => key.includes('v4'));

  var rows = null
  if (hasV4Key) {
    rows = [
      { protocol: 'MAnycast ICMPv4', data: characterization?.MAnycastICMPv4 },
      { protocol: 'MAnycast TCPv4', data: characterization?.MAnycastTCPv4 },
      { protocol: 'MAnycast UDPv4', data: characterization?.MAnycastUDPv4 },
      { protocol: 'iGreedy ICMPv4', data: characterization?.iGreedyICMPv4},
      { protocol: 'iGreedy TCPv4', data: characterization?.iGreedyTCPv4 }
    ];
}
  else{
    rows = [
      { protocol: 'MAnycast ICMPv6', data: characterization?.MAnycastICMPv6 },
      { protocol: 'MAnycast TCPv6', data: characterization?.MAnycastTCPv6 },
      { protocol: 'MAnycast UDPv6', data: characterization?.MAnycastUDPv6 },
      { protocol: 'iGreedy ICMPv6', data: characterization?.iGreedyICMPv6 },
      { protocol: 'iGreedy TCPv6', data: characterization?.iGreedyTCPv6 }
    ];
  }
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
            <td>{row.data?.anycast !== undefined ? (row.data.anycast ? 'Yes' : 'No') : 'N/A'}</td>
            <td>{row.data?.instances ?? 'N/A'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default CharacterizationTable;
