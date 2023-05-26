import React from "react";
import ModalOpinionsForVote from "./ModalOpinionsForVote";

function TeamsOpinionsForVote() {
  return (
    <div
      id="modal"
      className="flex flex-col justify-center items-center h-screen bg-black bg-opacity-30 z-10 inset-0"
    >
      <div className="flex flex-col w-[810px] h-[700px] rounded-card bg-white">
        <div className="flex items-center justify-center rounded-t-card bg-voteBar bg-cover text-white h-[105px]">
          <span className=" font-semibold text-4xl">
          1 Round 
          </span>
          <span className="ml-3 font-light text-4xl">
          Open Vote
          </span>
        </div>

        <div className="flex">
          <div className="flex flex-col w-2/4 ">
            <img
              src={require(`../../../images/chicken-g8k2s9.png`)}
              className="h-opinions-image"
              />
            <div className="flex items-center bg-card-normal-A pb-modal-opinions pt-aboveBest pr-modal-opinions pl-modal-opinions h-opinions-opinions">
              <div className="flex flex-col w-full justify-center">
                <ModalOpinionsForVote
                  data={{
                    team: "1",
                    rank: "01",
                    opinion:
                    "아...팀 잘못 선택함...",
                    likes: "541",
                  }}
                  />
                <ModalOpinionsForVote
                  data={{
                    team: "1",
                    rank: "02",
                    opinion:
                    "치킨도 소스 종류 진짜 많음",
                    likes: "136",
                  }}
                  />
                <ModalOpinionsForVote
                  data={{
                    team: "1",
                    rank: "03",
                    opinion:
                    "치킨에는 단백질이 많다",
                    likes: "104",
                  }}
                  />
              </div>
            </div>
          </div>

          <div className="flex flex-col w-2/4">
            <img
              src={require(`../../../images/pizza-z9c8y2.png`)}
              className=" rounded-tr-card h-opinions-image"
              />
            <div className="flex items-center bg-card-normal-B pb-modal-opinions pt-aboveBest pr-modal-opinions pl-modal-opinions h-opinions-opinions">
              <div className="flex flex-col w-full justify-center">
                <ModalOpinionsForVote
                  data={{
                    team: "2",
                    rank: "01",
                    opinion:
                    "닉값하러 옴",
                    likes: "431",
                  }}
                  />
                <ModalOpinionsForVote
                  data={{
                    team: "2",
                    rank: "02",
                    opinion:
                    "치킨보다 종류가 더 풍부함 ㄹㅇ",
                    likes: "230",
                  }}
                  />
                <ModalOpinionsForVote
                  data={{
                    team: "2",
                    rank: "03",
                    opinion:
                    "치즈 냠냠 굿~",
                    likes: "123",
                  }}
                  />
              </div>
            </div>
          </div>
        </div>
        <div className="flex rounded-b-card items-center justify-evenly h-[100px]">
          <button className="text-white bg-selected-A rounded-card h-[50px] w-[128px]">
            Keep
          </button>
          <div className="flex flex-col justify-center items-center">
            <div className=" text-sm font-extralight"> Change Team? </div>
            <div className=" text-lg font-bold">0:43</div>
          </div>
          <button className=" text-white bg-selected-B rounded-card h-[50px] w-[128px]">
            Change
          </button>
        </div>
      </div>
    </div>
  );
}

export default TeamsOpinionsForVote;
