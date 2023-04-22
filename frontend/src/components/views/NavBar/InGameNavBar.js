// import React, { Component, useEffect } from "react";

import { React, useEffect } from "react";

function InGameNavBar(props) {
    const teams = props.data.split(', ');
    const teamA = teams[0];
    const teamB = teams[1];
    useEffect(()=>{

    });
  return (
            <div className=" h-1/5">
                <nav className='flex justify-start bg-battleBar bg-center bg-contain bg-no-repeat'>
                    {/* <div className='text-lg px-8 py-6 leading-none bg-back-color text-white lg:mt-0 '>Naruhodoo</div>
                    <div className="text-3xl py-3 align-middle h-full w-full text-center">문, 바퀴 뭐가 더 많을까?</div> */}
                    <div className="flex flex-col w-full">
                        <div id="flow" className="text-center items-center m-auto h-1/2 w-full pt-10 text-white">
                            <span id="ready" className="px-3 py-2 border-2 border-white rounded-lg">준비</span>
                            <pre className="inline px-2">&gt;</pre>
                            <span id="open" className="px-3 py-2 border-white rounded-lg">공개</span>
                            <pre className="inline px-2">&gt;</pre>
                            <span id="vote" className="px-3 py-2 border-white rounded-lg">투표</span>
                        </div>
                        <div className="flex text-white text-4xl">
                            <span id="a" className="flex-shrink-0 text-center py-12 ml-auto mr-auto">{teamA}</span>
                            <span id="b" className="flex-shrink-0 text-center py-12 ml-auto mr-auto">{teamB}</span>
                        </div>
                    </div>
                </nav>
            </div>
  )
}

export default InGameNavBar