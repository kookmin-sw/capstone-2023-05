import React from 'react'

function ModalOpinionsForVote(props) {
    const data = props.data;
    const team = Number(data.team);
    const rank = data.rank;
    const opinion = data.opinion;
    const likes = Number(data.likes);
  return (
    <div className='flex h-20 my-3'>
        {/* 순위 */}
        <div className={`flex mr-4 justify-center items-center text-xl font-medium ${team === 1 ? 'text-selected-A' : 'text-selected-B'}`}>
            {rank}
        </div>
        {/* 내용 */}
        <div className={`flex p-4 w-full rounded-card border border-solid ${team === 1 ? ' bg-vote-selected-A border-vote-opinion-A-border' : 'bg-vote-selected-B border-vote-opinion-B-border'}`}>
            <div className=' text-xs overflow-auto'>
                {opinion}
            </div>
            <div className='flex flex-col justify-center items-center ml-auto pl-3'>
                <div className=' bg-fire w-5 h-5 border-none bg-cover rounded-full'/>
                <div className={`text-sm font-medium ${team === 1 ? 'text-selected-A' : 'text-selected-B'}`}>
                    {likes}
                </div>
            </div>
        </div>
    </div>
  )
}

export default ModalOpinionsForVote