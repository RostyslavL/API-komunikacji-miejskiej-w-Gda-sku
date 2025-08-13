import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import moment from "moment";

const API_URL = 'http://127.0.0.1:8000';

const Table = () => {
    const [stopName, setStopName] = useState('Brama Wyżynna');
    const [lineNumber, setLineNumber] = useState('');

    const fetchDepartures = async () => {
        let url = `${API_URL}/departures?stop_name=${encodeURIComponent(stopName)}${lineNumber ? `&routeId=${encodeURIComponent(lineNumber)}` : ''}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    };

    const { data, isLoading, error } = useQuery({
        queryKey: ['departures', stopName, lineNumber],
        queryFn: fetchDepartures,
    });

    const exportToJson = () => {
        if (!data) return;

        const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(data, null, 2))}`;
        const link = document.createElement('a');
        link.href = jsonString;
        link.download = `${stopName.replace(/\s+/g, '_')}${lineNumber ? `_route_${lineNumber}` : ''}_departures.json`;
        link.click();
    };

    return (
        <div className="p-4">
            <div className="mb-4 flex items-center gap-4">
                <label className="input">
                    <svg className="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <g
                            strokeLinejoin="round"
                            strokeLinecap="round"
                            strokeWidth="2.5"
                            fill="none"
                            stroke="currentColor"
                        >
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.3-4.3"></path>
                        </g>
                    </svg>
                    <input
                        type="search"
                        className="grow"
                        placeholder="Enter stop name"
                        value={stopName}
                        onChange={(e) => setStopName(e.target.value)}
                    />
                    <kbd className="kbd kbd-sm">⌘</kbd>
                    <kbd className="kbd kbd-sm">K</kbd>
                </label>
                <label className="input">
                    <svg className="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <g
                            strokeLinejoin="round"
                            strokeLinecap="round"
                            strokeWidth="2.5"
                            fill="none"
                            stroke="currentColor"
                        >
                        </g>
                    </svg>
                    <input
                        type="text"
                        className="grow"
                        placeholder="Provide Line Number"
                        value={lineNumber}
                        onChange={(e) => setLineNumber(e.target.value)}
                    />
                </label>
                <button onClick={exportToJson} className="btn btn-primary" disabled={!data}>
                    Export to JSON
                </button>
            </div>

            {isLoading && (
                <div className="loading loading-spinner loading-lg">
                    <span className="loading loading-spinner loading-xl"></span>
                </div>
            )}
            {error && (
                <div className="chat chat-end">
                    <div className="chat-bubble chat-bubble-error">
                        <div className="text-red-600">Error: {error.message}</div>
                    </div>
                </div>
            )}
            {data && (
                <>
                    <h2 className="mb-2 font-bold text-lg">
                        Departures for: {data.stopName}{data.routeId ? ` (Route ${data.routeId})` : ''}
                    </h2>
                    <div className="overflow-x-auto">
                        <table className="table w-full table-zebra">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Headsign</th>
                                    <th>Estimated Time (UTC)</th>
                                    <th>Estimated Local Time</th>
                                    <th>Theoretical Time</th>
                                    <th>Delay (sec)</th>
                                    <th>Route Short Name</th>
                                    <th>Status</th>
                                    <th>Vehicle Code</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.departures.map((dep, index) => (
                                    <tr key={`${dep.id}-${index}`}>
                                        <td>{dep.id}</td>
                                        <td>{dep.headsign}</td>
                                        <td>{moment(dep.estimatedTime).utc().format('YYYY-MM-DD, h:mm:ss')}</td>
                                        <td>{moment(dep.estimatedLocalTime).utc().format('YYYY-MM-DD, h:mm:ss')}</td>
                                        <td>{moment(dep.theoreticalTime).utc().format('YYYY-MM-DD, h:mm:ss')}</td>
                                        <td>{dep.delayInSeconds ?? '-'}</td>
                                        <td>{dep.routeShortName}</td>
                                        <td>{dep.status}</td>
                                        <td>{dep.vehicleCode ?? '-'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    );
};

export default Table;