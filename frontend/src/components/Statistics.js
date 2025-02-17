import React from "react";
import "./Statistics.css";
import Export from "./Export";

function Statistics({ data, timestamps, video }) {
  const calculatePercentage = (numerator, denominator) => {
    if (!denominator) return 0;
    return (numerator / denominator) * 100;
  };

  if (!data) {
    return (
      <div className="statistics">
        <h2>Statistics</h2>
        <div className="division" />
        <p>Processing video...</p>
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
  } = data;

  const totalContested = made_contested + missed_contested;
  const totalUncontested = made_uncontested + missed_uncontested;

  return (
    <div className="statistics">
      <h2>Statistics</h2>
      <div className="division" />
      
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Overall Shooting Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {calculatePercentage(makes, attempts).toFixed(1)}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">{attempts}</div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {`${makes}/${attempts}`}
            </div>
          </div>
        </div>
      </div>

      <div className="statisticsItem">
        <div className="statisticsItemTitle">Uncontested</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {calculatePercentage(made_uncontested, totalUncontested).toFixed(1)}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">{totalUncontested}</div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {`${made_uncontested}/${totalUncontested}`}
            </div>
          </div>
        </div>
      </div>

      <div className="statisticsItem">
        <div className="statisticsItemTitle">Contested</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {calculatePercentage(made_contested, totalContested).toFixed(1)}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">{totalContested}</div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {`${made_contested}/${totalContested}`}
            </div>
          </div>
        </div>
      </div>

      {timestamps && video && (
        <div className="export">
          <Export timestamps={timestamps} video={video} />
        </div>
      )}
    </div>
  );
}

export default Statistics;
