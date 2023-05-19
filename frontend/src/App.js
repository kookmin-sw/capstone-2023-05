import './App.css';
import React, {Component}from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";

import LandingPage from './components/views/LandingPage/LandingPage'
import LoginPage from './components/views/LoginPage/LoginPage'
import MakingRoomPage from './components/views/MakingRoomPage/MakingRoomPage'
import MyPage from './components/views/MyPage/MyPage'
import BattlePage from './components/views/BattlePage/BattlePage'
import BattlePageHost from './components/views/BattlePage/BattlePageHost'
import BeforeStart from './components/views/BeforeStart/BeforeStart'

class App extends Component {
  render(){
      return (
        <>
        <Router>
          <Routes>
          <Route exact path="/" element={<LandingPage />} />
            {/* <Route path="/makeRoom" element={<MakingRoomPage />} /> */}
            <Route path="/host" element={<BattlePageHost />} />
            <Route path="/makeRoom" element={<MakingRoomPage />} />
            <Route path="/mypage" element={<MyPage />} />
            <Route path="/game" element={<BattlePage />} />
            <Route path="/before" element={<BeforeStart />} />
          </Routes>
        </Router>
      </>
      );
  }
}

export default App;