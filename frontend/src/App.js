import "./App.css";
import LandingPage from "./components/views/LandingPage/LandingPage";
import TeamsOpinions from "./components/views/cardView/TeamsOpinions";
import MakingRoomPage from "./components/views/MakingRoomPage/MakingRoomPage";
import MyPage from "./components/views/MyPage/MyPage";
import Battle from "./components/views/Battle/Battle";
import { BattleProvider } from "context/battle";
import { Component } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BattlePageHost from "./components/views/BattlePage/BattlePageHost";
import Ready from "./components/views/Battle/Pages/Ready";

class App extends Component {
  render() {
    return (
      <>
        <Router>
          <Routes>
            <Route exact path="/" element={<LandingPage />} />
            {/* <Route path="/makeRoom" element={<MakingRoomPage />} /> */}
            <Route path="/host" element={<BattlePageHost />} />
            <Route path="/before" element={<Ready />} />
            <Route path="/makeRoom" element={<MakingRoomPage />} />
            <Route path="/mypage" element={<MyPage />} />
            <Route
              path="/game"
              element={
                <BattleProvider>
                  <Battle />
                </BattleProvider>
              }
            />
            <Route path="/before" element={<Ready />} />
            <Route path="/teamsOpinions" element={<TeamsOpinions />} />
          </Routes>
        </Router>
      </>
    );
  }
}

export default App;
