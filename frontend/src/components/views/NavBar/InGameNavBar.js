import { React, useEffect } from "react";

function InGameNavBar(props) {    
    const teams = props.data[0].split(', ');
    const teamA = teams[0];
    const teamB = teams[1];
    const teamId = Number(teams[2]);
    const round = props.data[1];

    useEffect(()=>{
        startTimer();
        if(teamId === 1){ 
            document.getElementById('b').classList.remove('text-2xl');
            document.getElementById('b').classList.add('text-xl');
            document.getElementById('b').classList.add('text-white');
            document.getElementById('b').classList.add('text-opacity-40');
        }
        else if(teamId === 2){
            document.getElementById('a').classList.remove('text-2xl');
            document.getElementById('a').classList.add('text-xl');
            document.getElementById('a').classList.add('text-white');
            document.getElementById('a').classList.add('text-opacity-40');
        }
        return () => clearInterval(roundTimer);
    },[]);
    
    let roundTimer;
    let roundSec = 180;
    
    function startTimer(){
        roundTimer = setInterval(countTimer, 1000);
    }
    
    const countTimer = ()=>{
        if(Number(roundSec) !== 0){
            roundSec--;
        }
        else{
            clearInterval(roundTimer);
        }
        
        document.getElementById('roundTimer').innerText = ((roundSec%60) < 10) ? parseInt(roundSec/60) + " : 0" + (roundSec%60) : parseInt(roundSec/60) + " : " + (roundSec%60);
    }
    
    


  return (
    // 비율같은 부분 추가 작업 필요
    <div className=" h-window-card bg-battleBar bg-center bg-cover bg-no-repeat">
        <nav className=' flex flex-col justify-start'>
            {/* <div className="flex flex-col w-full h-full"> */}
                <div id="flow" className="text-center items-center text-white mt-6">
                    <span id="ready" className="px-3 py-2 border-2 border-white rounded-lg">준비</span>
                    <pre className="inline px-2">&gt;</pre>
                    <span id="open" className="px-3 py-2 border-white rounded-lg">공개</span>
                    <pre className="inline px-2">&gt;</pre>
                    <span id="vote" className="px-3 py-2 border-white rounded-lg">투표</span>
                </div>
                <br/>
        </nav>
        <div className=" relative text-white text-4xl">
            <span id="a" className="absolute left-1/4 align-text-bottom pb-2 ml-10 text-2xl">
                <span className=" mr-3">
                    A team 
                </span>
                {teamA}
            </span>
            <span id="b" className="absolute right-1/4 align-text-bottom pb-2 mr-10 text-2xl">
                <span className=" mr-3">
                    B team 
                </span>
                {teamB}
            </span>
            <span className="absolute right-0 text-center pb-2 mr-20">
                <span className="text-2xl mr-3 left-0">
                    {round} round 
                </span>
                <span id="roundTimer">
                    3:00
                </span>
            </span>
        </div>
    </div>
  )
}

export default InGameNavBar