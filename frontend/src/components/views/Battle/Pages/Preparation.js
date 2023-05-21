import InGameNavBar from "components/views/NavBar/InGameNavBar";
import CardComponent from "components/views/cardView/CardComponent";
import { battleContext } from "context/battle";
import { useContext, useEffect, useState } from "react";

function sendOpinion(socket, round, input) {
  let data = { action: "sendOpinion", round: 1, opinion: input };
  socket.send(JSON.stringify(data)); // 서버로 메시지 전송
  console.log("[Preparation] sendOpinion", data);
}

const Preparation = ({ round }) => {
  const [input, setInput] = useState("");
  const {
    socketRef,
    battleState,
    currentRound,
    currentTeam,
    battleInfo,
    opinions,
    bestOpinion,
  } = useContext(battleContext);

  return (
    <div className="flex flex-col h-screen">
      {/* 채팅 UI 구현 */}
      <InGameNavBar data={`${"치킨"}, ${"피자"}`} />
      <div className=" w-screen h-time-bar bg-white">
        <img src="images/battleBar.png" alt="timer" />
      </div>
      <div className="flex flex-1 my-auto">
        {/* 좌측 광고 */}
        <div className="flex w-2/3 h-full bg-background-color">
          {/* opinions */}
          <div className="flex flex-col w-full h-full items-center pt-aboveBest">
            {/* best */}
            <div className="flex w-full">
              <div className=" mb-2">
                <button className=" bg-star bg-cover w-3 h-3 mr-3" />
                <span className=" font-bold mr-3">Best 3</span>
                <button className=" text-gray-500 text-xs underline">
                  Last
                </button>
              </div>
            </div>

            <div className="flex">
              {" "}
              {/* best opinions */}
              <CardComponent
                data={`${
                  battleInfo.nickname
                }, ${"동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산"}, ${123}`}
              />
              <CardComponent
                data={`${
                  battleInfo.nickname
                }, ${"동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산"}, ${123}`}
              />
              <CardComponent
                data={`${
                  battleInfo.nickname
                }, ${"동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산"}, ${123}`}
              />
            </div>

            {/* ads */}
            <div className="flex w-full">
              <div className=" mb-2">
                <button className=" bg-star bg-cover w-3 h-3 mr-3" />
                <span className=" font-bold mr-3">Ads</span>
              </div>
            </div>
            <div className="flex">
              {" "}
              {/* ads opinions */}
              <CardComponent
                data={`${
                  battleInfo.nickname
                }, ${"동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산"}, ${123}`}
              />
              <CardComponent
                data={`${
                  battleInfo.nickname
                }, ${"동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산"}, ${123}`}
              />
              <CardComponent
                data={`${
                  battleInfo.nickname
                }, ${"동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산"}, ${123}`}
              />
            </div>
          </div>

          {/* timer */}
          <div className=" flex font-bold pt-aboveBest mr-9 text-gray-500">
            0:59
          </div>
        </div>

        {/* 우측 채팅 바 */}
        <div className="flex flex-col w-1/3 bg-white h-full">
          <div className="flex flex-col w-full h-full"></div>
          {/* <div
            id="result"
            className="rounded text-md leading-none border-dotted border-x-4 border-y-4 border-back-color mx-5 my-5 px-1 py-1 inline-block"
          ></div> */}
          {/* 아래 채팅 박스 */}
          <div
            id="chat"
            className="flex mt-auto border-t-2 h-1/8 items-center justify-center"
          >
            <div className="flex items-center w-5/6 h-1/2">
              <input
                type="text"
                id="txt"
                className=" bg-background-color rounded-lg h-full w-sendChat px-2"
                placeholder="Enter your opinion"
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
              <button
                id="send"
                disabled={!input}
                className={
                  !input
                    ? "text-sm rounded-lg bg-gray-400 text-white ml-auto w-sendbtn h-full"
                    : " text-sm rounded-lg bg-sendBtn text-white ml-auto w-sendbtn h-full"
                }
                onClick={() => {
                  sendOpinion(socketRef.current, currentRound, input);
                }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Preparation;
