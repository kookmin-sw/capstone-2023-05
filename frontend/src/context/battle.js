import { createContext, useState, useEffect, useRef } from "react";

const WS_URL = "wss://rk07acynb6.execute-api.ap-northeast-2.amazonaws.com/dev";

const battleContext = createContext();

function BattleProvider({ children }) {
  const socketRef = useRef(null);

  const [battleState, setBattleState] = useState("init");
  const [battleInfo, setBattleInfo] = useState({
    battleId: "000002",
    userId: "newuser@gmail.com",
    nickname: "abc",
    isHost: false,
    teams: [
      {
        teamId: 1,
        teamName: "치킨",
      },
      {
        teamId: 2,
        teamName: "피자",
      },
    ],
  }); // battleId, userId, nickname

  const [currentRound, setCurrentRound] = useState(1);
  const [currentTeam, setCurrentTeam] = useState(1);

  const [opinions, setOpinions] = useState([]); // [{nickname, opinion}, ...
  const [ads, setAds] = useState([]); // [{nickname, content}, ...
  const [bestOpinions, setBestOpinions] = useState([]);

  // 배틀 페이지에 최초 라우팅 시 동작
  useEffect(() => {
    let ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          action: "initJoin",
          battleId: battleInfo.battleId,
          userId: battleInfo.userId,
          nickname: battleInfo.nickname,
        })
      );
      console.log("[BattleContext] initJoin");
    };

    ws.onclose = () => {
      console.log("[BattleContext] WebSocket disconnected");
    };

    ws.onerror = (err) => {
      console.error("[BattleContext] WebSocket error", err);
    };

    socketRef.current = ws;

    return () => {
      if (
        socketRef.current &&
        socketRef.current.readyState === WebSocket.OPEN
      ) {
        socketRef.current.close();
        socketRef.current = null;
        console.log("[BattleContext] Websocket Closed");
      }
    };
  }, [battleInfo.battleId, battleInfo.userId, battleInfo.nickname]);

  useEffect(() => {
    if (!socketRef.current) return;

    socketRef.current.onmessage = (event) => {
      console.log("[BattleContext] WebSocket message received", event);
      let message = JSON.parse(event.data);

      // action에 따른 분기 처리
      switch (message.action) {
        case "initJoinResult": // 방 접속 후 팀 정보 수신
          console.log("[BattleContext] initJoinResult");
          setBattleInfo((battleInfo) => ({
            battleId: battleInfo.battleId,
            userId: battleInfo.userId,
            nickname: battleInfo.nickname,
            teams: message.teams,
          }));
          setBattleState("Ready");
          break;

        // case startBattleBroadcast: // 호스트가 게임 시작
        // console.log("[BattleContext] startBattle");
        // setBattleState("initTeamSelect"); // 유저의 화면을 팀 선택으로 전환
        // break;

        case "voteResult":
          //todo
          break;

        case "currentRound": // startRound의 Broadcast
          console.log("[BattleContext] currentRound");
          // set currentRound as int
          setCurrentRound(message.round);
          break;

        case "preparationStart": // 준비 단계 시작 및 유저 화면 전환
          console.log("[BattleContext] preparationStart");
          setBattleState("Preparation");
          break;

        case "recvOpinion":
          console.log("[BattleContext] recvOpinion", message);
          setOpinions((opinions) => [
            ...opinions,
            { nickname: message.nickname, opinion: message.opinion },
          ]);
          console.log("[BattleContext] opinions", opinions);
          break;

        case "endRound":
          console.log("[BattleContext] endRound");
          setBattleState("endRound");
          break;

        case "endBattle":
          console.log("[BattleContext] endBattle");
          setBattleState("endBattle");
          break;

        default:
          console.log("[BattleContext] default");
          break;
      }
    };
  }, [opinions]);

  return (
    <battleContext.Provider
      value={{
        socketRef,
        battleState,
        currentRound,
        currentTeam,
        battleInfo,
        opinions,
        setOpinions,
        ads,
        setAds,
        bestOpinions,
        setBestOpinions,
      }}
    >
      {children}
    </battleContext.Provider>
  );
}

export { BattleProvider, battleContext };
