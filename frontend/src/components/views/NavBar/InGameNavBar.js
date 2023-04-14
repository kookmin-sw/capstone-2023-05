import React, { Component } from "react";

export default class InGameNavBar extends Component {

    render(){
        return (
            <>
                <nav className='flex justify-start'>
                    <div className='text-lg px-8 py-6 leading-none bg-back-color text-white lg:mt-0 '>Naruhodoo</div>
                    <div className="text-3xl py-3 align-middle h-full w-full text-center">문, 바퀴 뭐가 더 많을까?</div>
                </nav>
                <hr />
            </>
        )
    }
}
