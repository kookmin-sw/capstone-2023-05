import TeamCard from "../cardView/TeamCard";

// 팀 카드 2개 수평으로 나타내는 컴포넌트
function TeamCards({ teams, isHost, selectedTeam, setSelectedTeam }) {
  const handleTeamCardClick = (team) => {
    if (!isHost) setSelectedTeam(team);
    console.log("selectedTeam:", selectedTeam);
  };

  return (
    <div className="flex mt-select-team">
      <span
        id={teams[0].teamId}
        className={`border mr-16 rounded-card `}
        onClick={() => handleTeamCardClick(teams[0].teamId)}
      >
        <TeamCard
          teamId={teams[0].teamId}
          teamName={teams[0].teamName}
          teamImage={teams[0].image}
          isSelected={selectedTeam === teams[0].teamId}
          c="red"
        />
      </span>
      <span
        id={teams[1].teamId}
        className={`border ml-16 rounded-card `}
        onClick={() => handleTeamCardClick(teams[1].teamId)}
      >
        <TeamCard
          teamId={teams[1].teamId}
          teamName={teams[1].teamName}
          teamImage={teams[1].image}
          isSelected={selectedTeam === teams[1].teamId}
          c="blue"
        />
      </span>
    </div>
  );
}

export default TeamCards;
