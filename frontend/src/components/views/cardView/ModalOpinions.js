import React from 'react'

function ModalOpinions(props) {
    const data = props.data;
    const team = Number(data.team);
    const rank = data.rank;
    const opinion = data.opinion;
    const likes = Number(data.likes);

    console.log(data);
    console.log(team);
    console.log(rank);
    console.log(opinion);
    console.log(likes);
  return (
    <div className='flex h-20 mb-5'>
        {/* 순위 */}
        <div className={`flex mr-4 justify-center items-center text-xl font-medium ${team === 1 ? 'text-selected-A' : 'text-selected-B'}`}>
            {rank}
        </div>
        {/* 내용 */}
        <div className={`flex p-4 w-full rounded-card ${team === 1 ? 'bg-card-normal-A' : 'bg-card-normal-B'}`}>
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

export default ModalOpinions