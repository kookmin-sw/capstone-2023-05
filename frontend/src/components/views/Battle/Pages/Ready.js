import { useEffect, useState, useContext } from "react";
import TeamCards from "../../cardView/TeamCards";
import { battleContext } from "context/battle";

const SELECT_TIME = 5;

// player의 게임 시작 전 방 화면
function Ready() {
  const { socketRef, battleState, battleInfo, setBattleState } =
    useContext(battleContext);
  //   const battleState = "Ready";
  //   const socketRef = useRef();
  // const battleInfo = { battleInfo,isHost: false };
  // const battleState = "initTeamSelect";
  //   const battleInfo = { isHost: true };
  const [time, setTime] = useState(SELECT_TIME);
  const [selectedTeam, setSelectedTeam] = useState(0);

  useEffect(() => {
    if (battleState === "initTeamSelect") {
      // 1분 타이머
      const timer =
        time > 0 &&
        setInterval(() => {
          setTime((time) => time - 0.1);
        }, 100);

      if (time <= 0) {
        // 타이머 종료 시 vote
        socketRef.current.send(
          JSON.stringify({
            action: "vote",
            round: 0,
            teamId: `${
              selectedTeam
                ? selectedTeam
                : battleInfo.teams[randomIndex(1)].teamId
            }`,
          })
        );
        setBattleState("Preparation");
      }

      return () => clearInterval(timer);
    }
  }, [time, battleState, selectedTeam]);

  return (
    <div>
      <div className="flex flex-col items-center bg-beforeStart bg-cover w-screen h-screen">
        <div className="flex">
          {/** 양 팀카드 표시  */}
          <div className="flex">
            <TeamCards
              teams={battleInfo.teams}
              isHost={battleInfo.isHost}
              selectedTeam={selectedTeam}
              setSelectedTeam={setSelectedTeam}
            />
          </div>
        </div>

        {/* 방장 게임 시작 전 */}
        {/* <div className="flex pt-aboveBest">
          <div className="flex bg-players h-8 w-8 bg-cover" />
          <div className=" text-3xl ml-3">10</div>
        </div> */}

        {/* 일반 참가자일 경우, 방장 게임 시작 대기 */}
        {battleState === "Ready" && !battleInfo.isHost && (
          <div id="readyText" className=" text-3xl mt-36">
            방장이 게임을 시작하기를 기다리고 있습니다...
          </div>
        )}

        {/* 일반 참가자일 경우, 방장 게임 시작 시 정해진 시간동안 초기 팀 선택 */}
        {battleState === "initTeamSelect" && !battleInfo.isHost && (
          <>
            <div id="readyText" className=" text-3xl mt-24">
              그림을 눌러 팀을 선택하세요!
            </div>
          </>
        )}

        {/* 방장일 경우, 너비 166px, 높이 65, 색상 #5A2FB1, 텍스트 Start가 적힌 버튼 표시 */}
        {battleState === "Ready" && battleInfo.isHost && (
          <>
            <div id="readyText" className=" text-3xl mt-36">
              Start를 눌러 게임을 시작하세요!
            </div>
            <button
              onClick={() =>
                onStartBattleButtonClick(socketRef.current, battleInfo)
              }
              style={{
                marginTop: "2%",
                width: "166px",
                height: "65px",
                backgroundColor: "#5A2FB1",
                color: "white",
                fontSize: "26px",
                borderRadius: "10px",
              }}
            >
              Start
            </button>
          </>
        )}

        {/* 방장일 경우, 참가자의 팀 선택 대기 */}
        {battleState === "initTeamSelect" && battleInfo.isHost && (
          <div id="readyText" className=" text-3xl mt-24">
            참가자가 팀을 선택하는 중입니다...
          </div>
        )}

        {battleState === "initTeamSelect" && (
          <div id="readyToStartTimer" className=" text-5xl font-bold mt-8">
            {time > 0 ? `${time.toFixed(1)}초` : "로딩중..."}
          </div>
        )}
      </div>
    </div>
  );
}

function onStartBattleButtonClick(socket, battleInfo) {
  socket.send(
    JSON.stringify({
      action: "startBattle",
      battleId: battleInfo.battleId,
    })
  );
  setTimeout(() => {
    socket.send(
      JSON.stringify({
        action: "startRound",
        battleId: battleInfo.battleId,
      })
    );
    socket.send(
      JSON.stringify({
        action: "preparationStart",
        round: 1, // 첫 라운드
        battleId: battleInfo.battleId,
      })
    );
  }, (SELECT_TIME + 1) * 1000);
}

function randomIndex(max) {
  return Math.floor(Math.random() * max);
}

export default Ready;
