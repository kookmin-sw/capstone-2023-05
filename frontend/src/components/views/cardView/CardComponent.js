import React from 'react'

function CardComponent(props) {
    const opinions = props.data.split(', ');
    const nickname = opinions[0];
    const opinion = opinions[1];
    let likes = opinions[2];
  return (
    <div className='flex flex-col w-window-card h-window-card rounded-card bg-white'>
        <div className=' h-opinion px-5'>
            <div className=' py-2 font-semibold text-font'>
                {nickname}
            </div>
            <div className=' text-font'>
                {opinion}
            </div>
        </div>
        <div className='relative mt-auto rounded-b-card px-5 h-likes font-bold bg-card-normal text-card-text'>
            <div className='absolute inline transform translate-y-1/4 text-sm'>
                {likes}
            </div>
            <div className=' absolute inline -top-4 right-2'>
                <button className='bg-like rounded-full bg-cover border-none w-10 h-10'></button>
            </div>
        </div>
    </div>
  )
}

export default CardComponent