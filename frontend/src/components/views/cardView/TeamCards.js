import {React, useState} from 'react'
import TeamCard from '../cardView/TeamCard'

// 팀 카드 2개 수평으로 나타내는 컴포넌트
function TeamCards(props) {
    const status = props.data; // 'player' 또는 'host'
    const [selectedTeam, setSelectedTeam] = useState('');

    const handleTeamCardClick = (team) => {
        if(status === 'player')
            setSelectedTeam(team);
    };

    return (
      <div className='flex mt-select-team'>
        <span
          id='AteamCard'
          className={`border mr-16 rounded-card `}
          onClick={() => handleTeamCardClick('A')}
        >
          <TeamCard data={['치킨', 'chicken', 1]} state={selectedTeam} />
        </span>
        <span
          id='BteamCard'
          className={`border ml-16 rounded-card `}
          onClick={() => handleTeamCardClick('B')}
        >
          <TeamCard data={['피자', 'pizza', 2]} state={selectedTeam} />
        </span>
      </div>
    );
  }

export default TeamCards