import React from 'react'

function CardComponent(props) {
    const opinions = props.data.split(', ');
    const nickname = opinions[0];
    const opinion = opinions[1];
    let likes = opinions[2];
    const isBest = Number(opinions[3]);

  return (
    <div className='flex flex-col w-window-card h-window-card rounded-card bg-white mr-2'>
        <div className=' h-opinion px-5'>
            <div className=' py-2 font-semibold text-nickname'>
                {nickname}
            </div>
            <div className=' text-body scroll'>
                {opinion}
            </div>
        </div>
        {isBest ? (
        <div id='like' className='relative mt-auto rounded-b-card px-5 h-likes font-bold bg-bestLikes bg-cover text-white'>
            <div className='absolute inline transform translate-y-1/4 text-sm'>
                + {likes}
            </div>
            <div className=' absolute inline -top-4 right-2'>
                <button className='bg-like rounded-full bg-cover border-none w-10 h-10'></button>
            </div>
        </div>
        ) : (
        <div id='like' className='relative mt-auto rounded-b-card px-5 h-likes font-bold bg-card-normal bg-cover text-card-text'>
            <div className='absolute inline transform translate-y-1/4 text-sm'>
                + {likes}
            </div>
            <div className=' absolute inline -top-4 right-2'>
                <button className='bg-like rounded-full bg-cover border-none w-10 h-10'></button>
            </div>
        </div>
        )}
    </div>
  )
}

export default CardComponent