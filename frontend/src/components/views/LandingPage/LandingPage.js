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
          <BattleCard
            battleInfo={{
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
              title: "뭐가 더 맛있을까?",
              description: "치킨 vs 피자",
              host: "침착걸",
              participants: "1,234명",
            }}
          />
          <BattleCard
            battleInfo={{
              teamA: {
                teamName: "팀 A",
                teamImage:
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/L-door.png/800px-L-door.png",
              },
              teamB: {
                teamName: "팀 B",
                teamImage:
                  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQG3FImlyyis2L6erCk5COnUQ_wRBcZo0Laq3cZpnX8Nar8nNAblHaJLm-b_4qc1SqDbY8&usqp=CAU",
              },
              title: "뭐가 더 많을까?",
              description: "문 vs 바퀴",
              host: "주호밍",
              participants: "231명",
            }}
          />
          <BattleCard
            battleInfo={{
              teamA: {
                teamName: "팀 A",
                teamImage:
                  "https://media.istockphoto.com/id/1442902355/ko/벡터/빨간-머리-인어와-파란-빨간-꼬리-수영-인어-귀여운-인어-벡터-티셔츠-또는-어린이-책.jpg?s=612x612&w=0&k=20&c=ouZfrVbse9lkPmRMrxOdF9JPB9fjE6MvBU9xM3da5HI=",
              },
              teamB: {
                teamName: "팀 B",
                teamImage:
                  "https://t1.daumcdn.net/cfile/tistory/2602DF3C55C9C42B25",
              },
              title: "뭐가 더 나을까?",
              description: "인어 vs 어인",
              host: "디즈닝",
              participants: "1,328명",
            }}
          />
          <BattleCard
            battleInfo={{
              teamA: {
                teamName: "팀 A",
                teamImage:
                  "https://is3-ssl.mzstatic.com/image/thumb/ZypiNEdbU0wwCF0GMJ3zoA/1200x675mf.jpg",
              },
              teamB: {
                teamName: "팀 B",
                teamImage:
                  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoK6snfZiufQD7OOxH0bOhJnK5hYeCm7TWug&usqp=CAU",
              },
              title: "뭐가 더 명작일까?",
              description: "아이언맨 vs 다크나이트",
              host: "스파이더",
              participants: "3,432명",
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
