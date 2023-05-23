import React from 'react'

// 팀 카드 컴포넌트 & 클릭하면 테두리 색칠됨.
function TeamCard(props) {
    //props = {team 이름, 이미지, 어느 팀인지}
    const teamInfo = props.data;
    const teamName = teamInfo[0];
    const teamImage = teamInfo[1];
    const teamAB = Number(teamInfo[2]);
    const selectedTeam = props.state;
    console.log(teamAB, selectedTeam);
  return (
    <>
    {(teamAB === 1)?(
    <div className={`flex flex-col w-team-card h-team-card rounded-card p-1 shadow-lg shadow-red-300  ${selectedTeam === 'A' ? 'bg-selected-A' : 'bg-white'}`}>
        <img src={require(`../../../images/${teamImage}.png`)} className=' h-team-card-img bg-auto bg-red-100 pb-1 rounded-t-card' alt={teamName}/>
        <div className='flex items-center justify-center h-team-card-name bg-bestLikesA bg-cover rounded-b-card mt-auto text-white font-bold text-2xl'>
            {teamName}
        </div> 
    </div> 
        ):(
    <div className={`flex flex-col w-team-card h-team-card rounded-card p-1 shadow-lg shadow-blue-300 ${selectedTeam === 'B' ? 'bg-selected-B' : 'bg-white'}`}>
        <img src={require(`../../../images/${teamImage}.png`)} className=' h-team-card-img bg-auto bg-blue-100 pb-1 rounded-t-card' alt={teamName}/>
        <div className='flex items-center justify-center h-team-card-name bg-bestLikesB bg-cover rounded-b-card mt-auto text-white font-bold text-2xl'>
            {teamName}
        </div> 
    </div>
    )}
    </>
  )
}

export default TeamCard