import React, { useState } from "react";
import infoIcon from "../assets/infoIcon.png";
import "./Statistics.css";
import Export from "./Export";

function Statistics({ videoData, timestamps, video, report, runId }) {
  const [selectedTeam, setSelectedTeam] = useState("A");
  const [showInfo, setShowInfo] = useState(false);

  return (
    <div className="statistics">
      <div className="statisticsHeader">
        <div className="statisticsTitle">Statistics</div>
        <img
          className="statistics-infoIcon"
          onMouseEnter={() => setShowInfo(true)}
          onMouseLeave={() => setShowInfo(false)}
          src={infoIcon}
        />
        {showInfo && (
          <div className="statistics-infoOverlay">
            <div>
              Team-based statistics are only available for full-court matches
              with two camera angles.
            </div>
          </div>
        )}
      </div>
      <div className="division" />
      {videoData && videoData.isMatch && (
        <div className="statisticsTeams">
          <div
            className={selectedTeam === "A" ? "teamSelected" : "teamUnselected"}
            onClick={() => setSelectedTeam("A")}
          >
            Team A
          </div>
          <div
            className={selectedTeam === "B" ? "teamSelected" : "teamUnselected"}
            onClick={() => setSelectedTeam("B")}
          >
            Team B
          </div>
        </div>
      )}

      <div className="statisticsItem">
        <div className="statisticsItemTitle">Overall Shooting Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? (report.team_A.total_shooting_percentage * 100).toFixed(1)
                    : (report.team_B.total_shooting_percentage * 100).toFixed(1)
                  : (report.total_shooting_percentage * 100).toFixed(1)
                : "-"}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">
                {report
                  ? report.is_match
                    ? selectedTeam === "A"
                      ? report.team_A.total_attempts
                      : report.team_B.total_attempts
                    : report.total_attempts
                  : "-"}
              </div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? `${report.team_A.total_makes}/${report.team_A.total_attempts}`
                    : `${report.team_B.total_makes}/${report.team_B.total_attempts}`
                  : `${report.total_makes}/${report.total_attempts}`
                : "-/-"}
            </div>
          </div>
        </div>
      </div>
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Two-point Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? (report.team_A.two_pt_shooting_percentage * 100).toFixed(
                        1
                      )
                    : (report.team_B.two_pt_shooting_percentage * 100).toFixed(
                        1
                      )
                  : (report.two_pt_shooting_percentage * 100).toFixed(1)
                : "-"}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">
                {report
                  ? report.is_match
                    ? selectedTeam === "A"
                      ? report.team_A.two_pt_attempts
                      : report.team_B.two_pt_attempts
                    : report.two_pt_attempts
                  : "-"}
              </div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? `${report.team_A.two_pt_makes}/${report.team_A.two_pt_attempts}`
                    : `${report.team_B.two_pt_makes}/${report.team_B.two_pt_attempts}`
                  : `${report.two_pt_makes}/${report.two_pt_attempts}`
                : "-/-"}
            </div>
          </div>
        </div>
      </div>
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Three-Point Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? (
                        report.team_A.three_pt_shooting_percentage * 100
                      ).toFixed(1)
                    : (
                        report.team_B.three_pt_shooting_percentage * 100
                      ).toFixed(1)
                  : (report.three_pt_shooting_percentage * 100).toFixed(1)
                : "-"}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">
                {report
                  ? report.is_match
                    ? selectedTeam === "A"
                      ? report.team_A.three_pt_attempts
                      : report.team_B.three_pt_attempts
                    : report.three_pt_attempts
                  : "-"}
              </div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? `${report.team_A.three_pt_makes}/${report.team_A.three_pt_attempts}`
                    : `${report.team_B.three_pt_makes}/${report.team_B.three_pt_attempts}`
                  : `${report.three_pt_makes}/${report.three_pt_attempts}`
                : "-/-"}
            </div>
          </div>
        </div>
      </div>
      <div className="statisticsItem">
        <div className="statisticsItemTitle">Paint-Area Percentage</div>
        <div className="statisticsItemValue">
          <div className="shootingPercentage">
            <div className="number">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? (
                        report.team_A.paint_area_shooting_percentage * 100
                      ).toFixed(1)
                    : (
                        report.team_B.paint_area_shooting_percentage * 100
                      ).toFixed(1)
                  : (report.paint_area_shooting_percentage * 100).toFixed(1)
                : "-"}
              <span className="percentage">%</span>
            </div>
          </div>
          <div className="verticalDivider" />
          <div className="detailedShots">
            <div className="totalShots">
              <div className="shotNumber">
                {report
                  ? report.is_match
                    ? selectedTeam === "A"
                      ? report.team_A.paint_area_attempts
                      : report.team_B.paint_area_attempts
                    : report.paint_area_attempts
                  : "-"}
              </div>
              <div>&nbsp;SHOTS</div>
            </div>
            <div className="shotAttempts">
              {report
                ? report.is_match
                  ? selectedTeam === "A"
                    ? `${report.team_A.paint_area_makes}/${report.team_A.paint_area_attempts}`
                    : `${report.team_B.paint_area_makes}/${report.team_B.paint_area_attempts}`
                  : `${report.paint_area_makes}/${report.paint_area_attempts}`
                : "-/-"}
            </div>
          </div>
        </div>
      </div>
      {report && (
        <div className="export">
          <Export
            timestamps={timestamps}
            video={video}
            isMatch={report.is_match}
            runId={runId}
          />
        </div>
      )}
    </div>
  );
}

export default Statistics;
