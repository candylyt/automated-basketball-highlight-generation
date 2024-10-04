import React from "react";
import { ReactComponent as ExportIcon } from "../assets/exportIcon.svg";
import "./Statistics.css";

function Statistics() {
  return (
    <div className="statistics">
      <h2>Statistics</h2>
      <div className="division" />
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Shooting Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              56<span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">18</div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">10/18</div>
          </div>
        </div>
      </div>
      <div className="export">
        <div>Export</div>
        <ExportIcon className="exportIcon" />
      </div>
    </div>
  );
}

export default Statistics;
