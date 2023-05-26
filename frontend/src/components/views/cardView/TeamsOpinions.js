import React from "react";
import ModalOpinions from "./ModalOpinions";

function TeamsOpinions() {
  const modal = document.getElementById("modal");
  const modalOnOff = function () {
    modal.classList.add("hidden");
  };
  return (
    <div
      id="modal"
      className="flex flex-col justify-center items-center h-except-window-card bg-black bg-opacity-30 z-10 inset-0"
    >
      <div className="flex w-opinions-modal">
        <span
          className="close justify-start ml-auto text-gray-300 hover:text-gray-900 hover:cursor-pointer focus:text-gray-900 text-3xl"
          onClick={modalOnOff}
        >
          &times;
        </span>
      </div>
      <div className="flex w-opinions-modal h-opinions-modal border-solid rounded-card bg-white">
        <div className="flex flex-col w-2/4  border-solid border-r-2">
          <img
            src={require(`../../../images/chicken-g8k2s9.png`)}
            className=" rounded-tl-card h-opinions-image"
          />
          <div className="flex justify-center items-center h-opinions-team-name bg-selected-A text-white font-semibold">
            치킨
          </div>
          <div className="flex items-center pb-modal-opinions pt-aboveBest pr-modal-opinions pl-modal-opinions h-opinions-opinions">
            <div>
              <ModalOpinions
                data={{
                  team: "1",
                  rank: "01",
                  opinion:
                    "동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산",
                  likes: "1234",
                }}
              />
              <ModalOpinions
                data={{
                  team: "1",
                  rank: "02",
                  opinion:
                    "동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산",
                  likes: "1234",
                }}
              />
              <ModalOpinions
                data={{
                  team: "1",
                  rank: "03",
                  opinion:
                    "동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산",
                  likes: "1234",
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
          <div className="flex justify-center items-center h-opinions-team-name bg-selected-B text-white font-semibold">
            피자
          </div>
          <div className="flex items-center pb-modal-opinions pt-aboveBest pr-modal-opinions pl-modal-opinions h-opinions-opinions">
            <div>
              <ModalOpinions
                data={{
                  team: "2",
                  rank: "01",
                  opinion:
                    "동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산",
                  likes: "1234",
                }}
              />
              <ModalOpinions
                data={{
                  team: "2",
                  rank: "02",
                  opinion:
                    "동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산",
                  likes: "1234",
                }}
              />
              <ModalOpinions
                data={{
                  team: "2",
                  rank: "03",
                  opinion:
                    "동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산",
                  likes: "1234",
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TeamsOpinions;
