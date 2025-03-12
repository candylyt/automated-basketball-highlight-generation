import React, { useState } from "react";
import { ReactComponent as ExportIcon } from "../assets/exportIcon.svg";
import "./Statistics.css";
import Export from "./Export";
import { sumArray } from "./utils";

function Statistics({ data, videoData, timestamps, video }) {
  const [selectedTeam, setSelectedTeam] = useState("A");

  const calculatePercentage = (numerator, denominator) => {
    return (numerator / denominator) * 100;
  };

  return (
    <div className="statistics">
      <h2>Statistics</h2>
      <div className="division" />
      {videoData.isMatch && (
        <div className="statisticsTeams">
          <div
            className={selectedTeam === "A" ? "teamSelected" : "teamUnselected"}
            onClick={() => setSelectedTeam("A")}
          >
            Team A
          </div>
          <di
            className={selectedTeam === "B" ? "teamSelected" : "teamUnselected"}
            onClick={() => setSelectedTeam("B")}
          >
            Team B
          </di>
        </div>
      )}

      <div className="statisticsItem">
        <div className="statisticsItemTitle">Overall Shooting Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {data.makesA.length > 0 ||
              data.makesB.length > 0 ||
              data.attemptsA.length > 0 ||
              data.attemptsB.length > 0
                ? selectedTeam === "A"
                  ? calculatePercentage(
                      sumArray(data.makesA),
                      sumArray(data.attemptsA)
                    ).toFixed(1)
                  : calculatePercentage(
                      sumArray(data.makesB),
                      sumArray(data.attemptsB)
                    ).toFixed(1)
                : "-"}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">
                {data.makesA.length > 0 ||
                data.makesB.length > 0 ||
                data.attemptsA.length > 0 ||
                data.attemptsB.length > 0
                  ? selectedTeam === "A"
                    ? sumArray(data.attemptsA)
                    : sumArray(data.attemptsB)
                  : "-"}
              </div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {data.makesA.length > 0 ||
              data.makesB.length > 0 ||
              data.attemptsA.length > 0 ||
              data.attemptsB.length > 0
                ? selectedTeam === "A"
                  ? `${sumArray(data.makesA)}/${sumArray(data.attemptsA)}`
                  : `${sumArray(data.makesB)}/${sumArray(data.attemptsB)}`
                : "-/-"}
            </div>
          </div>
        </div>
      </div>
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Uncontested</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {data.makesA.length > 0 ||
              data.makesB.length > 0 ||
              data.attemptsA.length > 0 ||
              data.attemptsB.length > 0
                ? selectedTeam === "A"
                  ? calculatePercentage(
                      sumArray(data.makesA),
                      sumArray(data.attemptsA)
                    ).toFixed(1)
                  : calculatePercentage(
                      sumArray(data.makesB),
                      sumArray(data.attemptsB)
                    ).toFixed(1)
                : "-"}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">
                {data.makesA.length > 0 ||
                data.makesB.length > 0 ||
                data.attemptsA.length > 0 ||
                data.attemptsB.length > 0
                  ? selectedTeam === "A"
                    ? sumArray(data.attemptsA)
                    : sumArray(data.attemptsB)
                  : "-"}
              </div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {data.makesA.length > 0 ||
              data.makesB.length > 0 ||
              data.attemptsA.length > 0 ||
              data.attemptsB.length > 0
                ? selectedTeam === "A"
                  ? `${sumArray(data.makesA)}/${sumArray(data.attemptsA)}`
                  : `${sumArray(data.makesB)}/${sumArray(data.attemptsB)}`
                : "-/-"}
            </div>
          </div>
        </div>
      </div>
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Contested</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {data.makesA.length > 0 ||
              data.makesB.length > 0 ||
              data.attemptsA.length > 0 ||
              data.attemptsB.length > 0
                ? selectedTeam === "A"
                  ? calculatePercentage(
                      sumArray(data.makesA),
                      sumArray(data.attemptsA)
                    ).toFixed(1)
                  : calculatePercentage(
                      sumArray(data.makesB),
                      sumArray(data.attemptsB)
                    ).toFixed(1)
                : "-"}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">
                {data.makesA.length > 0 ||
                data.makesB.length > 0 ||
                data.attemptsA.length > 0 ||
                data.attemptsB.length > 0
                  ? selectedTeam === "A"
                    ? sumArray(data.attemptsA)
                    : sumArray(data.attemptsB)
                  : "-"}
              </div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {data.makesA.length > 0 ||
              data.makesB.length > 0 ||
              data.attemptsA.length > 0 ||
              data.attemptsB.length > 0
                ? selectedTeam === "A"
                  ? `${sumArray(data.makesA)}/${sumArray(data.attemptsA)}`
                  : `${sumArray(data.makesB)}/${sumArray(data.attemptsB)}`
                : "-/-"}
            </div>
          </div>
        </div>
      </div>
      {(data.makesA.length > 0 ||
        data.makesB.length > 0 ||
        data.attemptsA.length > 0 ||
        data.attemptsB.length > 0) && (
        <div className="export">
          {/* <div>Export</div>
        <ExportIcon className="exportIcon" /> */}
          <Export
            timestamps={timestamps}
            video={video}
            isMatch={videoData.isMatch}
          />
        </div>
      )}
    </div>
  );
}

export default Statistics;
