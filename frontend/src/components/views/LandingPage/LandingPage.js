import React from "react";
import { Card, Container } from "semantic-ui-react";
import LobbyNavBar from "../NavBar/LobbyNavBar";
import BattleCard from "../cardView/BattleCard";

function LandingPage() {
  return (
    <div className=" bg-gray-200 min-h-screen">
      <LobbyNavBar />
      <div className=" container mx-auto ">
        <div className=" px-20 flex flex-wrap gap-5 justify-center pt-10 ">
          <BattleCard />
          <BattleCard />
          <BattleCard />
          <BattleCard />
          <BattleCard />
          <BattleCard />
          <BattleCard />
          <BattleCard />
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
