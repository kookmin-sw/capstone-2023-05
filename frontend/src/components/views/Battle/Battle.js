import Preparation from "./Pages/Preparation";
import Discussion from "./Pages/Discussion";
import Ready from "./Pages/Ready";
import { battleContext } from "context/battle";
import React, { useContext } from "react";

const Battle = (props) => {
  const { battleState } = useContext(battleContext);

  switch (battleState) {
    case "Ready":
    case "initTeamSelect":
      console.log("[BattleState] Ready");
      return <Ready />;
    case "Preparation":
      console.log("[BattleState] Preparation");
      return <Preparation />;
    case "Discussion":
      console.log("[BattleState] Discussion");
      return <Discussion />;
    case "MidResult":
      console.log("[BattleState] midResult");
      return <div>midResult</div>;
    case "finishBattle":
      console.log("[BattleState] finishBattle");
      return <div>FinalResult</div>;
    default:
      console.log("[BattleState] unknown state:", battleState);
      break;
  }
};

export default Battle;
