import { useEffect, useState, useContext } from "react";
import TeamCards from "../../cardView/TeamCards";
import { battleContext } from "context/battle";

// player의 게임 시작 전 방 화면
function FinalResult() {
  const battleInfo = {
    teams: [
      {
        teamId: 1,
        teamName: "치킨",
        image:
          "https://naruhodoo-team-image.s3.ap-northeast-2.amazonaws.com/chicken-g8k2s9.png",
      },
      {
        teamId: 2,
        teamName: "피자",
        image:
          "https://naruhodoo-team-image.s3.ap-northeast-2.amazonaws.com/pizza-z9c8y2.png",
      },
    ],
    isHost: false,
  };

  return (
    <div className=" bg-redWin min-h-screen ">
      <div className="flex flex-col justify-center items-center pt-60">
        <div className="text-3xl font-bold text-black">Final Result</div>
        <div className="flex flex-row justify-center items-center pt-10">
          <div className="text-5xl font-bold text-black">뭐가 더 맛있나요?</div>
        </div>
        <img alt="result" src="result-red-chicken-win.png" className="pt-10" />
      </div>
    </div>
  );
}

export default FinalResult;
