import React, {Component}from "react";
import {
  // BrowserRouter as Router,
  // Routes,
  // Route,
  Link
} from "react-router-dom";

export default class LobbyNavBar extends Component {
  customButton = {
    'display' : 'inline',
    'marginTop' : '0.9rem',
    'marginRight' : '10px',
    'marginBottom' : '0.9rem',
    'textAlign' : 'center',
    'verticalAlign' : 'middle',
    'height' : '100%'
  }
  render() {
    return (
      <>
        <nav className='flex justify-start'>
          <Link to="/" className=' text-lg px-8 py-6 leading-none bg-back-color text-white lg:mt-0 '>Naruhodoo</Link>
          <Link to="/makeRoom" style={this.customButton} className=' text-sm px-4 py-2 leading-none border rounded bg-back-color text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mt-0 mb-0 ml-auto'>방 만들기</Link>
          <Link to="/before" style={this.customButton} className=' text-sm px-4 py-2 leading-none border rounded bg-back-color text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mt-0 mb-0 ml-5'>시작 전 방 선택</Link>
          <Link to="/host" style={this.customButton} className=' text-sm px-4 py-2 leading-none border rounded bg-back-color text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mt-0 mb-0 ml-5'>호스트</Link>
          <Link to="/game" style={this.customButton} className=' text-sm px-4 py-2 leading-none border rounded bg-back-color text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mt-0 mb-0 ml-5'>게임</Link>
        </nav>
      <hr />
    </>
    )
  }
}
