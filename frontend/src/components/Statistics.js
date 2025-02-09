import React from "react";
import { ReactComponent as ExportIcon } from "../assets/exportIcon.svg";
import "./Statistics.css";
import Export from "./Export";

function Statistics({data, timestamps, video}) {
  const calculatePercentage = (numerator, denominator) => {
    return (numerator / denominator) * 100;
  };

  if (!data) {
    return (
      <div className="statistics">
        <h2>Statistics</h2>
        <div className="division" />
        <div className="statisticsItem">
          <div className="statisticsItemTitle">Overall Shooting Percentage</div>
          <div className="statisticsItemValue">
            <div className="shootingPercentage">
              <div className="number">
                -
                <span className="percentage">%</span>
              </div>
            </div>
            <div className="verticalDivider" />
            <div className="detailedShots">
              <div className="totalShots">
                <div className="shotNumber">-</div>
                <div>&nbsp;SHOTS</div>
              </div>
              <div className="shotAttempts">-/-</div>
            </div>
          </div>
        </div>
        <div className="statisticsItem">
          <div className="statisticsItemTitle">Uncontested</div>
          <div className="statisticsItemValue">
            <div className="shootingPercentage">
              <div className="number">
                -
                <span className="percentage">%</span>
              </div>
            </div>
            <div className="verticalDivider" />
            <div className="detailedShots">
              <div className="totalShots">
                <div className="shotNumber">-</div>
                <div>&nbsp;SHOTS</div>
              </div>
              <div className="shotAttempts">-/-</div>
            </div>
          </div>
        </div>
        <div className="statisticsItem">
          <div className="statisticsItemTitle">Contested</div>
          <div className="statisticsItemValue">
            <div className="shootingPercentage">
              <div className="number">
                -
                <span className="percentage">%</span>
              </div>
            </div>
            <div className="verticalDivider" />
            <div className="detailedShots">
              <div className="totalShots">
                <div className="shotNumber">-</div>
                <div>&nbsp;SHOTS</div>
              </div>
              <div className="shotAttempts">-/-</div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="statistics">
      <h2>Statistics</h2>
      <div className="division" />
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Overall Shooting Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {calculatePercentage(data.makes, data.attempts).toFixed(1)}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">{data.attempts}</div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">{data.makes}/{data.attempts}</div>
          </div>
        </div>
      </div>
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Uncontested</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {calculatePercentage(data.makes, data.attempts).toFixed(1)}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">{data.attempts}</div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">{data.makes}/{data.attempts}</div>
          </div>
        </div>
      </div>
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Contested</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {calculatePercentage(data.makes, data.attempts).toFixed(1)}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">{data.attempts}</div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">{data.makes}/{data.attempts}</div>
          </div>
        </div>
      </div>
      <div className="export">
        {/* <div>Export</div>
        <ExportIcon className="exportIcon" /> */}
        <Export timestamps={timestamps} video={video}/>
      </div>
    </div>
  );
}

export default Statistics;
