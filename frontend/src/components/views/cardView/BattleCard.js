import React from "react";
import { Link } from "react-router-dom";

// 팀 카드 컴포넌트 & 클릭하면 테두리 색칠됨.
function BattleCard() {
  const battleInfo = {
    teamA: {
      teamName: "팀 A",
      teamImage:
        "https://images.unsplash.com/photo-1546272989-40c92939c6c2?ixid=M3wzODUwMTd8MHwxfHNlYXJjaHw3fHxjaGlja2VufGVufDB8MHx8fDE2ODUwMDU4NDl8MA&ixlib=rb-4.0.3",
    },
    teamB: {
      teamName: "팀 B",
      teamImage:
        "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?ixid=M3wzODUwMTd8MHwxfHNlYXJjaHw5fHxwaXp6YXxlbnwwfDB8fHwxNjg1MDA1ODI4fDA&ixlib=rb-4.0.3",
    },
  };

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
            <h1 className=" font-bold "> 뭐가 더 맛있을까? </h1>
            <h2 className=" text-gray-700 "> 치킨 vs 피자 </h2>
          </div>
          <div className=" flex flex-row justify-between pt-4">
            <p className=" text-gray-700 "> 침착맨 </p>
            <p className=" text-purple-800 "> 1,234명 </p>
          </div>
        </div>
      </Link>
    </>
  );
}

export default BattleCard;
