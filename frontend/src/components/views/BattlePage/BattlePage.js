import React, { useEffect, useState, useRef } from 'react';
import InGameNavBar from '../NavBar/InGameNavBar'
import CardComponent from '../cardView/CardComponent'

const ChatComponent = (props) => {
  const [message, setMessage] = useState('');
  
  const dev = 'wss://rd1hl7qgfi.execute-api.ap-northeast-2.amazonaws.com/dev';
  const functionRef = useRef(null);

  let battleId;
  let email;
  let nickname;
  let round;

  let recvData;
  // const battleId = '1234';
  // const email = 'example@gmail.com'
  // const nickname = 'nick'
  // let round = 1;

  const socket = new WebSocket(dev);
  useEffect(() => {

      // WebSocket에 연결
      // 웹소켓 연결이 열렸을 때 이벤트 핸들러
    socket.addEventListener('open', (event) => {
      console.log('WebSocket 연결이 열렸습니다.', event);
      
      // 서버로 데이터 전송
      socket.send(JSON.stringify({
        'action': 'initJoin', 
        'battleId': battleId, 
        'userId': email, 
        'nickname': nickname}));
      // socket.send('안녕하세요, 서버에게 메시지를 보냅니다!');
      console.log('sent');

    });

    // 웹소켓 메시지 수신 이벤트 핸들러
    socket.addEventListener('message', (event) => {
      console.log('WebSocket으로부터 메시지를 수신하였습니다.', event);
      recvData = JSON.parse(event.data.split());
      // 서버로부터 수신한 메시지 처리
      console.log('수신한 메시지:', recvData['message']);
      document.getElementById('result').innerHTML = 'message : ' + recvData['message'];
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
  
  // 메시지 전송 이벤트 핸들러
  functionRef.current = () => {
    // console.log('qwwrq2rqweafadsc');
    socket.send(JSON.stringify({'action':'sendOpinion', 'round': round, 'opinion': message})); // 서버로 메시지 전송
    console.log(`Message: ${message}  Sent`);
    setMessage(''); // 메시지 입력 필드 초기화
  };

  
  // 컴포넌트 렌더링
  return (
    <div className='flex flex-col h-screen'>
      {/* 채팅 UI 구현 */}
      <InGameNavBar data={`${'치킨'}, ${'피자'}`}/>
      <div className='flex flex-row flex-1 my-auto'>
        {/* 좌측 광고 */}
        <div className='flex flex-col items-center w-2/3 bg-background-color h-full pt-aboveBest'>
          <div className='flex'> {/* best */}
            <CardComponent data={`${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}`}/>
            <CardComponent data={`${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}`}/>
            <CardComponent data={`${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}`}/>
          </div>
          <div className='flex'> {/* ads */}
            <CardComponent data={`${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}`}/>
            <CardComponent data={`${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}`}/>
            <CardComponent data={`${nickname}, ${'동해물과 백두산이 마르고 닳도록 하나님이 보우하사 우리나라 만세 무궁화 삼천리 화려 강산 무궁화 삼천리 화려 강산 강산'}, ${123}`}/>
          </div>
        </div>

        {/* 우측 채팅 바 */}
        <div className='flex flex-col w-1/3 bg-white h-full'> 
          <div id='result' className='rounded text-md leading-none border-dotted border-x-4 border-y-4 border-back-color mx-5 my-5 px-1 py-1 inline-block'></div>
          {/* 아래 채팅 박스 */}
          <div id='chat' className='flex mt-auto border-t-2 h-1/8 items-center justify-center'>
            <div className='flex items-center w-5/6 h-1/2'>
              <input type="text" id='txt' className=' bg-background-color rounded-lg h-full w-sendChat px-2' placeholder='Enter your opinion' value={message} onChange={(e) => setMessage(e.target.value)} />
              <button id='send' disabled={!message} className={!message?'text-sm rounded-lg bg-gray-400 text-white ml-auto w-sendbtn h-full':' text-sm rounded-lg bg-sendBtn text-white ml-auto w-sendbtn h-full'} onClick={functionRef.current}>Send</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;


