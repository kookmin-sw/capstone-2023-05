import React, { useEffect, useState } from 'react';
import InGameNavBar from '../NavBar/InGameNavBar'
import CardComponent from '../cardView/CardComponent'
import TeamsOpinions from '../cardView/TeamsOpinions'

const ChatComponentHost = (props) => {
  const [message, setMessage] = useState('');
  const [value, setValue] = useState(0);
  const maxValue = 180; // 3분 = 180초
  const interval = 60; // 1분 = 60초

  const dev = 'wss://rd1hl7qgfi.execute-api.ap-northeast-2.amazonaws.com/dev';
  // const dev = 'wss://4a6dvup00h.execute-api.ap-northeast-2.amazonaws.com/jwlee';

  // 서버로부터 받을 데이터
  let recvData;
  const battleId = '000001';
  const userId = 'user123@example.com'
  const nickname = 'hoon'
  const teamId = "0"; // 팀 아이디 {teamA : 1, teamB : 2, host : ?}
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
    return () => clearInterval(timer);
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
    setMessage(''); // 메시지 입력 필드 초기화
  };
  
  const handleKeyPress = (event) => {
    if(event.code === 'Enter' && message !== ''){
      messageSend();
    }
  }

  const modal = document.getElementById('modal');
  const modalOnOff = function(){
      modal.classList.remove('hidden');
      modal.classList.add('absolute');
  }

  // 컴포넌트 렌더링
  return (
    <div className='flex flex-col h-screen'>
      {/* 채팅 UI 구현 */}
      {/* 상단 배너 */}
      <InGameNavBar data={[`${'치킨'}, ${'피자'}, ${teamId}`,round]}/>
      {/* 타이머 게이지 */}
      <div className="relative h-2 bg-white">
        <div className="absolute top-0 left-0 h-full bg-gradient-to-r from-white to-blue-500" style={{ width: `${(value / maxValue) * 100}%` }} />
        {[...Array(Math.floor(maxValue / interval)).keys()].map(i => (
            <div key={i} className="absolute top-1/2 transform -translate-y-1/2 h-2 w-1 bg-white" style={{ left: `${((i + 1) * interval / maxValue) * 100}%` }} />
        ))}
      </div>
      <div className='flex flex-1 my-auto'>
        <div id='modal' className='hidden w-screen mt-window-card z-10 inset-0'>
          <TeamsOpinions/>
        </div>
        {/* 좌측 광고 */}
        <div className='flex w-1/2 h-full bg-background-color'>
          {/* opinions */}
          <div className='flex flex-col w-5/6 h-full ml-opinion items-center pt-aboveBest'>
              {/* best */}
            <div className='flex w-full'>
              <div className=' mb-2'>
                <div className=' inline-block bg-star bg-cover w-3 h-3 mr-3 cursor-not-allowed'/>
                <span className=' font-bold mr-3'>Best 3</span>
                <button className='last text-gray-500 text-xs underline' onClick={modalOnOff}>Last</button>
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
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${1}`, `${'사자'}`, `${'피자 2조각(300g) 섭취 시`, `나트륨은 1,311.56mg으로 1일 영양소 기준치 2,000mg의 65.6%`, `포화지방은 13.36g으로 1일 영양소 기준치 15g의'}`, `${76}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'염소'}`, `${'솔직히 배달 시켜먹으면 피자는 마진 너무한거 아니냐;;'}`, `${78}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'낙타'}`, `${'KFC 할아버지 맛 못 잊제~'}`, `${23}`, `${0}`]}/>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${1}`, `${'재규어'}`, `${'황올`, `뿌링클`, `자메이카`, `고추바사삭`, `스노윙`, `청양마요,,`, `이걸 참아?'}`, `${123}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'고릴라'}`, `${'아침 점심 저녁으로 치킨 먹어도 안질림. 내가 해봄 아무튼 해봄 꼬우면 연락하셈 0101-03290-2495'}`, `${56}`, `${0}`]}/>
              <CardComponent data={[`${1}`, `${'범고래'}`, `${'???: 쿠쿠썸 츀흰'}`, `${8}`, `${0}`]}/>
            </div>
          </div>

        </div>
        {/* 우측 광고 */}
        <div className='flex w-1/2 h-full bg-background-color'>
          {/* opinions */}
          <div className='flex flex-col w-5/6 h-full items-center pt-aboveBest'>
              {/* best */}
            <div className='flex w-full'>
              <div className=' mb-2'>
                <div className=' inline-block bg-star bg-cover w-3 h-3 mr-3 cursor-not-allowed'/>
                <span className=' font-bold mr-3'>Best 3</span>
                <button className='last text-gray-500 text-xs underline' onClick={modalOnOff}>Last</button>
              </div>
            </div>

            <div className='flex w-full'> {/* best opinions */}
              <CardComponent data={[`${2}`, `${'암탉'}`, `${'닉값하러 옴'}`, `${431}`, `${1}`]}/>
              <CardComponent data={[`${2}`, `${'비둘기'}`, `${'치킨보다 더 종류가 풍부함 ㄹㅇ'}`, `${230}`, `${1}`]}/>
              <CardComponent data={[`${2}`, `${'젖소'}`, `${'치즈 냠냠 굿~'}`, `${123}`, `${1}`]}/>
            </div>
      
            {/* ads */}
            <div className='flex w-full pt-aboveAds'>
              <div className=' inline-block bg-star bg-cover w-3 h-3 mr-3'/>
              <span className=' font-bold mr-3'>무작위 의견</span>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${2}`, `${'오랑우탄'}`, `${'ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ'}`, `${12}`, `${0}`]}/>
              <CardComponent data={[`${2}`, `${'잡스'}`, `${'개발자는 다 식은 피자지'}`, `${253}`, `${0}`]}/>
              <CardComponent data={[`${2}`, `${'청둥오리'}`, `${'근본 양식 아님? 치킨 무근본 엌ㅋㅋㅋㅋ'}`, `${67}`, `${0}`]}/>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${2}`, `${'버팔로'}`, `${'가격이 곧 품격이다. 프리미엄 치킨? 피자보다 싸다!'}`, `${72}`, `${0}`]}/>
              <CardComponent data={[`${2}`, `${'소'}`, `${'소는 누가 키워'}`, `${3}`, `${0}`]}/>
              <CardComponent data={[`${2}`, `${'이구아나'}`, `${'손에 덜 묻어서 깔끔하게 먹기 쌉가능'}`, `${92}`, `${0}`]}/>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={[`${2}`, `${'거미'}`, `${'조각이 많아서 여러 명이서 나눠먹기 좋아.'}`, `${137}`, `${0}`]}/>
              <CardComponent data={[`${2}`, `${'갈치'}`, `${'아 팀 잘못 선택함'}`, `${1}`, `${0}`]}/>
              <CardComponent data={[`${2}`, `${'이탈리아'}`, `${'피자 만세'}`, `${266}`, `${0}`]}/>
            </div>
          </div>

          {/* timer */}
          <span id='adsTimer' className=' flex font-bold pt-aboveBest w-full text-gray-500'>1:00</span>
        </div>

      </div>
    </div>
  );
};

export default ChatComponentHost;


