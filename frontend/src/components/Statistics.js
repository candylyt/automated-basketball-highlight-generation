import React, { useState, useEffect } from "react";
import "./Statistics.css";
import Export from "./Export";

function Statistics({ data, timestamps, video }) {
  const [historicalData, setHistoricalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // If we have a timestamp, try to fetch historical data
    if (timestamps && timestamps.length > 0) {
      setLoading(true);
      fetch(`/get_statistics/${timestamps[timestamps.length - 1]}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch statistics');
          return res.json();
        })
        .then(data => {
          setHistoricalData(data);
          setError(null);
        })
        .catch(err => {
          setError(err.message);
          console.error('Error fetching statistics:', err);
        })
        .finally(() => setLoading(false));
    }
  }, [timestamps]);

  const calculatePercentage = (numerator, denominator) => {
    if (!denominator) return 0;
    return (numerator / denominator) * 100;
  };

  // Show loading state
  if (loading) {
    return (
      <div className="statistics">
        <h2>Statistics</h2>
        <div className="division" />
        <div className="loading-spinner">Loading statistics...</div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="statistics">
        <h2>Statistics</h2>
        <div className="division" />
        <div className="error-message">
          Error loading statistics. Please try again.
        </div>
      </div>
    );
  }

  // Use current data or historical data
  const statsData = data || historicalData;

  if (!statsData) {
    return (
      <div className="statistics">
        <h2>Statistics</h2>
        <div className="division" />
        <p>Waiting for video processing...</p>
      </div>
    );
  }

  // Extract data with default values
  const {
    attempts = 0,
    makes = 0,
    made_contested = 0,
    made_uncontested = 0,
    missed_contested = 0,
    missed_uncontested = 0
  } = statsData;

  const totalContested = made_contested + missed_contested;
  const totalUncontested = made_uncontested + missed_uncontested;

  const statItems = [
    {
      title: "Overall Shooting",
      makes: makes,
      attempts: attempts,
      className: "overall"
    },
    {
      title: "Uncontested Shots",
      makes: made_uncontested,
      attempts: totalUncontested,
      className: "uncontested"
    },
    {
      title: "Contested Shots",
      makes: made_contested,
      attempts: totalContested,
      className: "contested"
    }
  ];

  return (
    <div className="statistics">
      <h2>Shot Analysis</h2>
      <div className="division" />
      
      <div className="stats-container">
        {statItems.map((item, index) => (
          <div key={index} className={`statisticsItem ${item.className}`}>
            <div className="statisticsItemTitle">{item.title}</div>
            <div className="statisticsItemValue">
              <div className="shootingPercentage">
                <div className="number">
                  {calculatePercentage(item.makes, item.attempts).toFixed(1)}
                  <span className="percentage">%</span>
                </div>
              </div>
              <div className="verticalDivider" />
              <div className="detailedShots">
                <div className="totalShots">
                  <div className="shotNumber">{item.attempts}</div>
                  <div className="shotLabel">SHOTS</div>
                </div>
                <div className="shotAttempts">
                  {`${item.makes}/${item.attempts}`}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {timestamps && video && (
        <div className="export-container">
          <Export timestamps={timestamps} video={video} />
        </div>
      )}
    </div>
  );
}

export default Statistics;
