import React from 'react'
import TeamCards from '../cardView/TeamCards'

// player의 게임 시작 전 방 화면
function BeforeStart() {
  return (
    <div>
        <div className='flex flex-col items-center bg-beforeStart bg-cover w-screen h-screen'>
            <div className='flex'>{/** 양 팀카드 표시  */}
                <div className='flex'>
                    <TeamCards data={'player'}/>
                </div>
            </div>

        {/* 방장 게임 시작 전 */}
            <div className='flex pt-aboveBest'>
                <div className='flex bg-players h-8 w-8 bg-cover' />
                <div className=' text-3xl ml-3'>10</div>
            </div>

            <div id='beforeStart' className=' text-3xl mt-8'>
                방장이 게임을 시작하기 기다리고 있습니다...
            </div>
        {/* */}

        {/* 게임 시작 후 팀 선택 시간 */}
            <div className='flex flex-col items-center pt-aboveBest'>
                <div className=' text-3xl ml-3 font-light'>Start</div>
                <div id='readyToStartTimer' className=' text-5xl ml-3 mt-3'>1:00</div>
            </div>
        {/* */}
        </div>
    </div>
  )
}

export default BeforeStart