import React from "react";
import { Link } from "react-router-dom";

// 팀 카드 컴포넌트 & 클릭하면 테두리 색칠됨.
function BattleCard({ battleInfo }) {
  return (
    <>
      <Link to="/game">
        <div className=" flex-col w-56 rounded-card p-6 shadow-lg bg-white">
          <div className="flex flex-row justify-between">
            <img
              alt="teamA"
              className="w-1/2 pr-1"
              src={battleInfo.teamA.teamImage}
            />
            <img
              alt="teamB"
              className="w-1/2 pl-1"
              src={battleInfo.teamB.teamImage}
            />
          </div>
          <div className=" flex flex-col pt-4 gap-2">
            <h1 className=" font-bold "> {battleInfo.title} </h1>
            <h2 className=" text-gray-700 "> {battleInfo.description} </h2>
          </div>
          <div className=" flex flex-row justify-between pt-4">
            <p className=" text-gray-700 "> {battleInfo.host} </p>
            <p className=" text-purple-800 "> {battleInfo.participants} </p>
          </div>
        </div>
      </Link>
    </>
  );
}

export default BattleCard;
