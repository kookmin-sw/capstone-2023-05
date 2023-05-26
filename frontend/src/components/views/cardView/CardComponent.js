import React from 'react'

function CardComponent(props) {
    //props = {teamId, nickname, opinion, 좋아요 수, best의견인지}
    const opinions = props.data.split(', ');
    const teamId = Number(opinions[0]);
    const nickname = opinions[1];
    const opinion = opinions[2];
    let likes = opinions[3];
    const isBest = Number(opinions[4]);

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
        <>
        {(teamId === 1) && 
            ((isBest) ? // best인지 ads인지 구별해서 카드 표현
                (<div id='like' className='relative mt-auto rounded-b-card px-5 h-likes font-bold bg-bestLikesA bg-cover text-white'>
                    <div className='absolute inline transform translate-y-1/4 text-sm'>
                        + {likes}
                    </div>
                    <div className=' absolute inline -top-4 right-2'>
                        <button className='bg-like rounded-full bg-cover border-none w-10 h-10'></button>
                    </div>
                </div>)
                :
                (<div id='like' className='relative mt-auto rounded-b-card px-5 h-likes font-bold bg-card-normal-A bg-cover text-card-text-A'>
                    <div className='absolute inline transform translate-y-1/4 text-sm'>
                        + {likes}
                    </div>
                    <div className=' absolute inline -top-4 right-2'>
                        <button className='bg-like rounded-full bg-cover border-none w-10 h-10'></button>
                    </div>
                </div>)
            )
        }
        {(teamId === 2) && 
            ((isBest) ?
                (<div id='like' className='relative mt-auto rounded-b-card px-5 h-likes font-bold bg-bestLikesB bg-cover text-white'>
                    <div className='absolute inline transform translate-y-1/4 text-sm'>
                        + {likes}
                    </div>
                    <div className=' absolute inline -top-4 right-2'>
                        <button className='bg-like rounded-full bg-cover border-none w-10 h-10'></button>
                    </div>
                </div>
            ):(
                <div id='like' className='relative mt-auto rounded-b-card px-5 h-likes font-bold bg-card-normal-B bg-cover text-card-text-B'>
                    <div className='absolute inline transform translate-y-1/4 text-sm'>
                        + {likes}
                    </div>
                    <div className=' absolute inline -top-4 right-2'>
                        <button className='bg-like rounded-full bg-cover border-none w-10 h-10'></button>
                    </div>
                </div>
            ))
        }
        </>
    </div>
  )
}

export default CardComponent