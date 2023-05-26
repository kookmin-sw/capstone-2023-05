import React, { Component } from "react";
import {
  // BrowserRouter as Router,
  // Routes,
  // Route,
  Link,
} from "react-router-dom";

export default class LobbyNavBar extends Component {
  customButton = {
    display: "inline",
    marginTop: "0.9rem",
    marginRight: "10px",
    marginBottom: "0.9rem",
    textAlign: "center",
    verticalAlign: "middle",
    height: "100%",
  };
  render() {
    return (
      <nav className="flex justify-start bg-cover bg-lobbyBar ">
        <div className="container mx-auto py-4 flex flex-row ">
          <Link
            to="/"
            className=" text-2xl font-bold italic leading-none text-white lg:mt-0 "
          >
            Naruhodoo
          </Link>
          <div className="ml-auto">
            <Link
              to="/makeRoom"
              style={this.customButton}
              className=" text-sm px-4 py-2 leading-none border rounded bg-transparent text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mb-0 "
            >
              방 만들기
            </Link>
            <Link
              to="/before"
              style={this.customButton}
              className=" text-sm px-4 py-2 leading-none border rounded bg-transparent text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mb-0 ml-5"
            >
              시작 전 방 선택
            </Link>
            <Link
              to="/host"
              style={this.customButton}
              className=" text-sm px-4 py-2 leading-none border rounded bg-transparent text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mb-0 ml-5"
            >
              호스트
            </Link>
            <Link
              to="/game"
              style={this.customButton}
              className=" text-sm px-4 py-2 leading-none border rounded bg-transparent text-white border-white hover:border-transparent hover:text-gray-800 hover:bg-white hover:border-back-color mb-0 ml-5"
            >
              게임
            </Link>
          </div>
        </div>
      </nav>
    );
  }
}
