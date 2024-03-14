import React, { useState } from 'react';

interface CSVTableProps {
  csvData: string;
}

const CSVTable: React.FC<CSVTableProps> = ({ csvData }) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const rowsPerPage: number = 5;

  // Parse CSV data
  const rows = csvData.split('\n').slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage).map((row, rowIndex) => (
    <tr key={rowIndex}>
      {row.split(',').map((cell, cellIndex) => (
        <td key={cellIndex} className="border px-4 py-2">{cell}</td>
      ))}
    </tr>
  ));

  // Pagination controls
  const totalPages = Math.ceil(csvData.split('\n').length / rowsPerPage);
  const pagination = (
    <div className="flex justify-center mt-4">
      <button className="px-4 py-2 mr-2 bg-gray-200" onClick={() => setCurrentPage(currentPage - 1)} disabled={currentPage === 1}>Previous</button>
      <span>{`Page ${currentPage} of ${totalPages}`}</span>
      <button className="px-4 py-2 ml-2 bg-gray-200" onClick={() => setCurrentPage(currentPage + 1)} disabled={currentPage === totalPages}>Next</button>
    </div>
  );

  return (
    <div className="overflow-x-auto max-w-lg">
      <table className="table-auto w-full max-w-lg mx-auto">
        <tbody>
          {rows}
        </tbody>
      </table>
      {pagination}
    </div>
  );
};

export default CSVTable;
