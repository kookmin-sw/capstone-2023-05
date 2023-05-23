import React, { useEffect, useRef, useState } from 'react';
import InGameNavBar from '../NavBar/InGameNavBar'
import CardComponent from '../cardView/CardComponent'
import TeamsOpinions from '../cardView/TeamsOpinions'

const ChatComponent = (props) => {
  const [message, setMessage] = useState('');
  const [value, setValue] = useState(0);
  const maxValue = 180; // 3분 = 180초
  const interval = 60; // 1분 = 60초

  const dev = 'wss://rd1hl7qgfi.execute-api.ap-northeast-2.amazonaws.com/dev';

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
      modal.classList.add('absolute');
      modal.classList.remove('hidden');
  }
  
  // 컴포넌트 렌더링
  return (
    <div className='flex flex-col h-screen'>
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
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${1}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${1}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${1}`}/>
            </div>
      
            {/* ads */}
            <div className='flex w-full pt-aboveAds'>
              <div className=' inline-block bg-star bg-cover w-3 h-3 mr-3'/>
              <span className=' font-bold mr-3'>Ads</span>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
            </div>
            <div className='flex w-full mt-2'> {/* ads opinions */}
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
              <CardComponent data={`${1}, ${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}, ${0}`}/>
            </div>
          </div>

          {/* timer */}
          <span id='adsTimer' className=' flex font-bold pt-aboveBest w-full justify-center text-gray-500'>1:00</span>
        </div>

        {/* 우측 채팅 바 */}
        <div className='flex flex-col w-1/3 bg-white h-full'> 
          <div id='result' className='text-md h-7/8 items-baseline leading-none m-5 px-1 py-1 inline-block'></div>
          {/* 아래 채팅 박스 */}
          <div id='chat' className='flex border-t-2 h-1/8 items-center justify-center'>
            <div className='flex items-center w-5/6 h-1/2'>
              <input type="text" id='txt' className=' bg-background-color rounded-lg h-full w-sendChat px-2' placeholder='Enter your opinion' value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={handleKeyPress} />
              <button id='send' disabled={!message} className={!message?'text-sm rounded-lg bg-gray-400 text-white ml-auto w-sendbtn h-full':' text-sm rounded-lg bg-sendBtn text-white ml-auto w-sendbtn h-full'} onClick={messageSend}>Send</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;


