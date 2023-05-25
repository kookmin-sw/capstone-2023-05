import "./App.css";
import LandingPage from "./components/views/LandingPage/LandingPage";
import TeamsOpinions from "./components/views/cardView/TeamsOpinions";
import MakingRoomPage from "./components/views/MakingRoomPage/MakingRoomPage";
import MyPage from "./components/views/MyPage/MyPage";
import BattlePage from "./components/views/BattlePage/BattlePage";
import BattlePageForVote from "./components/views/BattlePage/BattlePageForVote";
import TeamsOpinionsForVote from "./components/views/cardView/TeamsOpinionsForVote";
import { BattleProvider } from "context/battle";
import { Component } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BattlePageHost from "./components/views/BattlePage/BattlePageHost";
import Ready from "./components/views/Battle/Pages/Ready";
import FinalResult from "components/views/Battle/Pages/FinalResult";

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
            <Route path="/vote" element={<BattlePageForVote />} />
            <Route
              path="/game"
              element={
                <BattleProvider>
                  <BattlePage />
                </BattleProvider>
              }
            />
            <Route path="/result" element={<FinalResult />} />
            <Route path="/before" element={<Ready />} />
            <Route path="/teamsOpinions" element={<TeamsOpinions />} />
          </Routes>
        </Router>
      </>
    );
  }
}

export default App;
