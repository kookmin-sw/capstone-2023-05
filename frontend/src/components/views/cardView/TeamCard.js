import React from "react";

const colorset = {
  red: {
    border: "bg-selected-A",
    shadow: "shadow-red-300",
    label: "bg-bestLikesA",
  },
  blue: {
    border: "bg-selected-B",
    shadow: "shadow-blue-300",
    label: "bg-bestLikesB",
  },
};

// 팀 카드 컴포넌트 & 클릭하면 테두리 색칠됨.
function TeamCard({ teamId, teamName, teamImage, isSelected, c }) {
  return (
    <>
      <div
        className={`flex flex-col w-team-card h-team-card rounded-card p-1 shadow-lg ${
          colorset[c].shadow
        } ${isSelected ? colorset[c].border : "bg-white"}`}
      >
        <img
          src={teamImage}
          className=" h-team-card-img bg-auto bg-red-100 pb-1 rounded-t-card"
          alt={teamName}
        />
        <div
          className={`flex items-center justify-center h-team-card-name ${colorset[c].label} bg-cover rounded-b-card mt-auto text-white font-bold text-2xl`}
        >
          {teamName}
        </div>
      </div>
    </>
  );
}

export default TeamCard;
