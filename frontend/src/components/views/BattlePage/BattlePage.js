import React, { useEffect, useRef, useState } from 'react';
import InGameNavBar from '../NavBar/InGameNavBar'
import CardComponent from '../cardView/CardComponent'
import TeamsOpinions from '../cardView/TeamsOpinions'

const ChatComponent = (props) => {
  const [message, setMessage] = useState('');
  const [opinions, setOpinions] = useState([]);
  const [value, setValue] = useState(0);
  const maxValue = 180; // 3분 = 180초
  const interval = 60; // 1분 = 60초

  const dev = 'wss://rk07acynb6.execute-api.ap-northeast-2.amazonaws.com/dev';

  // 서버로부터 받을 데이터
  let recvData;

  const battleId = '000001';
  const userId = 'user123@example.com'
  const nickname = 'hoon'
  const teamId = "1"; // 팀 아이디 {teamA : 1, teamB : 2, host : ?}
  let round = 1;
  
  const socket = new WebSocket(dev);
  useEffect(() => {
    // 웹소켓 연결이 열렸을 때 이벤트 핸들러
    socket.addEventListener('open', (event) => {
      console.log('WebSocket 연결이 열렸습니다.', event);
      
      // 서버에 연결
      socket.send(JSON.stringify({
        'action': 'initJoin', 
        'battleId': battleId, 
        'userId': userId, 
        'nickname': nickname}));
        console.log('sent');
      });
      
      // 웹소켓 메시지 수신 이벤트 핸들러
      socket.addEventListener('message', (event) => {
        console.log('WebSocket으로부터 메시지를 수신하였습니다.', event);
        recvData = JSON.parse(event.data.split());
        console.log(recvData);
        // 서버로부터 수신한 메시지 처리
        console.log('수신한 메시지:', recvData['message']);
        if(recvData['action'] === 'recvOpinion')
          document.getElementById('result').innerHTML += `\n${recvData['nickname']} : ${recvData['opinion']}`;
      });

      // 웹소켓 연결이 닫혔을 때 이벤트 핸들러
      socket.addEventListener('close', (event) => {
        console.log('Server에서 disconnection이 와서 WebSocket 연결이 닫혔습니다.', event);
      });
      
      // 웹소켓 에러 이벤트 핸들러
      socket.addEventListener('error', (event) => {
        console.error('WebSocket 에러가 발생하였습니다.', event);
      });
      
      // 컴포넌트 언마운트 시 소켓 연결 해제
      return () => {
        if(socket.readyState === socket.OPEN)
          socket.close();
      console.log("클라이언트에서 연결을 끊습니다.");
    };
  }, []);
  
  //광고판 타이머 변수
  let timer;  
  let adsSec = 60;

  // 광고판 타이머 시작 함수
  function startTimer(){
    timer = setInterval(countTimer, 1000);
  }

  // 타이머 동작함수
  const countTimer = ()=>{
    if(Number(adsSec) !== 0){
        adsSec--;
    }
    else{
      clearInterval(timer);
    }
    document.getElementById('adsTimer').innerText = (adsSec%60 < 10) ? parseInt(adsSec/60) + " : 0" + (adsSec%60) : parseInt(adsSec/60) + " : " + (adsSec%60)
  }

  useEffect(()=>{
    startTimer();
    return()=>{
      clearInterval(timer);
    }
  },[]);

  // 상단배너 아래 타이머 게이지 관련 useEffect
  useEffect(() => {
    const timer = setInterval(() => {
    setValue(prevValue => {
        if (prevValue >= maxValue) {
        clearInterval(timer);
        return maxValue;
        }
        return prevValue + 1;
    });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 메시지 전송 이벤트 핸들러
  const messageSend = () => {
    socket.send(JSON.stringify({'action':'sendOpinion', 'round': round, 'opinion': message})); // 서버로 메시지 전송
    console.log(`Message: ${message}  Sent`);
    
    // 입력 내용 채팅창에 하드코딩
    const newOpinion = JSON.stringify({nickname:"상어", opinion:message});
    setOpinions((prevOpinions) => [...prevOpinions, newOpinion]);
    
    setMessage(''); // 메시지 입력 필드 초기화
  };
  
  const handleKeyPress = (event) => {
    if(event.code === 'Enter' && message !== ''){
      messageSend();
    }
  }

  const modal = document.getElementById('modal');
  const modalOnOff = function(){
      modal.classList.add('absolute');
      modal.classList.remove('hidden');
  }

  useEffect(()=>{
    const result = document.getElementById('result');
    result.scrollTop = result.scrollHeight;
    console.log(`opinions : ${opinions}\n`);
  }, [opinions])
  
  // 컴포넌트 렌더링
  return (
    <div className="flex flex-col h-screen">
      {/* 채팅 UI 구현 */}
      {/* 상단 배너 */}
      <InGameNavBar data={[`${'치킨'}, ${'피자'}, ${teamId}`,round]}/>
      {/* 타이머 게이지 */}
      <div className="relative h-2 bg-white">
        <div className="absolute top-0 left-0 h-full bg-gradient-to-r from-white to-red-500" style={{ width: `${(value / maxValue) * 100}%` }} />
        {[...Array(Math.floor(maxValue / interval)).keys()].map(i => (
            <div key={i} className="absolute top-1/2 transform -translate-y-1/2 h-2 w-1 bg-white" style={{ left: `${((i + 1) * interval / maxValue) * 100}%` }} />
        ))}
      </div>
      <div className='flex flex-1 my-auto'>
        {/* 좌측 광고 */}
        <div className='flex w-2/3 h-full bg-background-color'>
          <div id='modal' className='hidden w-2/3 mt-window-card z-10 inset-0'>
            <TeamsOpinions/>
          </div>
          {/* opinions */}
          <div className='flex flex-col w-5/6 h-full ml-opinion items-center pt-aboveBest'>
              {/* best */}
            <div className='flex w-full'>
              <div className=' mb-2'>
                <div className=' inline-block bg-star bg-cover w-3 h-3 mr-3 cursor-not-allowed'/>
                <span className=' font-bold mr-3'>Best 3</span>
                <button className=' text-gray-500 text-xs underline' onClick={modalOnOff}>Last</button>
              </div>
            </div>

            <div className='flex w-full'> {/* best opinions */}
              <CardComponent data={[`${1}`, `${'닭'}`, `${'아...팀 잘못 선택함...'}`, `${541}`, `${1}`]}/>
              <CardComponent data={[`${1}`, `${'강아지'}`, `${'치킨도 소스 종류 진짜 많음'}`, `${136}`, `${1}`]}/>
              <CardComponent data={[`${1}`, `${'곰'}`, `${'치킨에는 단백질이 많다'}`, `${104}`, `${1}`]}/>
            </div>

            {/* ads */}
            <div className='flex w-full pt-aboveAds'>
              <div className=' inline-block bg-star bg-cover w-3 h-3 mr-3'/>
              <span className=' font-bold mr-3'>무작위 의견</span>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${1}`, `${'사자'}`, `${'치킨 영양성분 ▲열량 253.72kcal ▲단백질 18.77g ▲포화지방 2.86g ▲나트륨 408.19mg'}`, `${12}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'호랑이'}`, `${'단백질 ㅇㅈ'}`, `${25}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'병아리'}`, `${'아...'}`, `${6}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'침팬지'}`, `${'바나나가 더 맛있지'}`, `${1}`, `${0}`]}/>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${1}`, `${'사자'}`, `${'피자 2조각(300g) 섭취 시`, `나트륨은 1,311.56mg으로 1일 영양소 기준치 2,000mg의 65.6%`, `포화지방은 13.36g으로 1일 영양소 기준치 15g의'}`, `${76}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'염소'}`, `${'솔직히 배달 시켜먹으면 피자는 마진 너무한거 아니냐;;'}`, `${78}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'퐁당'}`, `${'한강 치킨 vs 한강 피자'}`, `${25}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'낙타'}`, `${'KFC 할아버지 맛 못 잊제~'}`, `${23}`, `${0}`]}/>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${1}`, `${'판다'}`, `${'세상에 나쁜 치킨은 없다!'}`, `${22}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'재규어'}`, `${'황올`, `뿌링클`, `자메이카`, `고추바사삭`, `스노윙`, `청양마요,,`, `이걸 참아?'}`, `${123}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'고릴라'}`, `${'아침 점심 저녁으로 치킨 먹어도 안질림. 내가 해봄 아무튼 해봄 꼬우면 연락하셈 0101-03290-2495'}`, `${56}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'범고래'}`, `${'???: 쿠쿠썸 츀흰'}`, `${8}`, `${0}`]}/>
            </div>
          </div>

          {/* timer */}
          <div id='adsTimer' className=' flex font-bold pt-aboveBest mr-9 w-12 text-gray-500'>1:00</div>

        </div>

        {/* 우측 채팅 바 */}
        <div className='flex flex-col w-1/3 bg-white h-full'> 
          <button onClick={()=>{
            const newOpinion = JSON.stringify({nickname:"강아지", opinion:"치킨에도 피자 토핑만큼 소스 많음"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion]);
            const newOpinion2 = JSON.stringify({nickname:"고양이", opinion:"당연히 치느님 아님? 피느님이라는 말 없잖슴 아ㅋㅋ"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion2]);
            const newOpinion3 = JSON.stringify({nickname:"토끼", opinion:"치킨이 올라간 피자도 있는데 그러면 피자가 다 쌈싸먹는거 아니냐?"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion3]);
            const newOpinion4 = JSON.stringify({nickname:"곰", opinion:"치킨에는 단백질이 많다"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion4]);
            const newOpinion5 = JSON.stringify({nickname:"호랑이", opinion:"단백질 ㅇㅈ"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion5]);
            const newOpinion6 = JSON.stringify({nickname:"사자", opinion:"도배 ㄴㄴ"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion6]);
            const newOpinion7 = JSON.stringify({nickname:"코끼리", opinion:"ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion7]);
            const newOpinion8 = JSON.stringify({nickname:"토끼", opinion:"근데 아버지가 퇴근하시고 사오는 통닭은 킹정이지 ㅋㅋ"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion8]);
            const newOpinion9 = JSON.stringify({nickname:"참치", opinion:"치킨은 먹다보면 물림 ㄹㅇ"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion9]);
            const newOpinion10 = JSON.stringify({nickname:"호랑이", opinion:"라떼는,,,전기. 구이. 통닭이. 최고다... 이거야... 요즘 것들은,,, 떼잉 쯧,,,,,,"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion10]);
            const newOpinion11 = JSON.stringify({nickname:"코끼리", opinion:"닭가슴살도 치킨 아님?"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion11]);
            const newOpinion12 = JSON.stringify({nickname:"고양이", opinion:"피자가 아무리 맛있다한들, 피자는 탄수화물이 주여서 살 엄청 찌고 치킨은 단백질이 주여서 근성장에 도움되는거 모름?"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion12]);
            const newOpinion13 = JSON.stringify({nickname:"아나콘다", opinion:"웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! 웅~치킨! "});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion13]);
            const newOpinion14 = JSON.stringify({nickname:"방울뱀", opinion:"치킨치킨치킨치킨치킨치킨치킨치킨치킨치킨치킨치킨치킨치킨치킨"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion14]);
            const newOpinion15 = JSON.stringify({nickname:"범고래", opinion:"ㅋㅋㅋㅋㅋㅋㅋㅋㅋ"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion15]);
            const newOpinion16 = JSON.stringify({nickname:"사자", opinion:"도배 자제좀"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion16]);
            const newOpinion17 = JSON.stringify({nickname:"연어", opinion:"3대 느님. 연느님, 유느님, 치느님"});
            setOpinions((prevOpinions) => [...prevOpinions, newOpinion17]);
          }}>add new opinion</button>
          <div id='result' className='flex flex-col text-sm h-7/8 mt-auto leading-none m-3 p-1 border border-solid overflow-y-auto max-h-chat'>
            {opinions.map((item, index) => (
              <div key={index} className={`flex ${index==0 ? 'mt-auto' : ''} text-gray-800 px-4 py-2`}>
                <div className=' inline-block w-1/8'>
                  {JSON.parse(item).nickname}
                </div>
                <div className=' inline-block w-7/8'>
                  {JSON.parse(item).opinion}
                </div>
              </div>
            ))}
          </div>
          {/* 아래 채팅 박스 */}
          <div id='chat' className='flex mt-auto border-t-2 h-1/8 items-center justify-center'>
            <div className='flex items-center w-5/6 h-1/2'>
              <input type="text" id='txt' className=' bg-background-color rounded-lg h-full w-sendChat px-2' placeholder='Enter your opinion' value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={handleKeyPress} />
              <button id='send' disabled={!message} className={`text-sm rounded-lg text-white ml-auto w-sendbtn h-full ${!message?' bg-gray-400':' bg-sendBtn'}`} onClick={messageSend}>Send</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;
