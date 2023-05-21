import React from "react";

function Ready({ isReady, onReadyClick, playerScore, opponentScore }) {
  return (
    <div className="bg-cover bg-center flex flex-col items-center justify-center h-screen">
      <div className="bg-contain bg-no-repeat h-1/2 w-1/2 flex flex-col items-center justify-center">
        <p className="text-4xl font-bold mb-2">
          {playerScore} : {opponentScore}
        </p>
        <p className="text-xl">
          {isReady ? "Waiting for opponent..." : "Click Ready to start!"}
        </p>
      </div>
      {!isReady && (
        <button
          className="mt-4 px-4 py-2 rounded-md bg-blue-500 text-white"
          onClick={onReadyClick}
        >
          Ready
        </button>
      )}
    </div>
  );
}

export default Ready;
