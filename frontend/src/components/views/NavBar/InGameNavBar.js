// import React, { Component, useEffect } from "react";

import { React, useEffect } from "react";

function InGameNavBar(props) {
    const teams = props.data.split(', ');
    const teamA = teams[0];
    const teamB = teams[1];
    useEffect(()=>{

    });
  return (
    // 비율같은 부분 추가 작업 필요
    <div className=" h-window-card bg-battleBar bg-center bg-cover bg-no-repeat">
        <nav className='h-full flex flex-col justify-center'>
            {/* <div className="flex flex-col w-full h-full"> */}
                <div id="flow" className="text-center items-center text-white mt-6">
                    <span id="ready" className="px-3 py-2 border-2 border-white rounded-lg">준비</span>
                    <pre className="inline px-2">&gt;</pre>
                    <span id="open" className="px-3 py-2 border-white rounded-lg">공개</span>
                    <pre className="inline px-2">&gt;</pre>
                    <span id="vote" className="px-3 py-2 border-white rounded-lg">투표</span>
                </div>
                <br/>
                <div className="flex text-white text-4xl">
                    <span id="a" className="flex-shrink-0 text-center pb-2 ml-auto mr-auto">{teamA}</span>
                    <span id="b" className="flex-shrink-0 text-center pb-2 ml-auto mr-auto">{teamB}</span>
                </div>
            {/* </div> */}
        </nav>
    </div>
  )
}

export default InGameNavBar