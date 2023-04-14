import React, { useEffect, useState, useRef } from 'react';
import InGameNavBar from '../NavBar/InGameNavBar'
// import {io} from "socket.io-client"

const ChatComponent = () => {
  const [message, setMessage] = useState('');
  const jw = 'wss://4a6dvup00h.execute-api.ap-northeast-2.amazonaws.com/jwlee';
  // const hoon = 'wss://xb11zrc3ta.execute-api.ap-northeast-2.amazonaws.com/hoon';
  const functionRef = useRef(null);
  const battleId = '1234';
  const email = 'example@gmail.com'
  const nickname = 'nick'

  
  useEffect(() => {
    // WebSocket에 연결
    const socket = new WebSocket(jw);
    
    // 웹소켓 연결이 열렸을 때 이벤트 핸들러
    socket.addEventListener('open', (event) => {
      console.log('WebSocket 연결이 열렸습니다.', event);
      
      // 서버로 데이터 전송
      socket.send('안녕하세요, 서버에게 메시지를 보냅니다!');
    });

    
    // 웹소켓 메시지 수신 이벤트 핸들러
    socket.addEventListener('message', (event) => {
      console.log('WebSocket으로부터 메시지를 수신하였습니다.', event);
      let dat = JSON.parse(event.data);
      // 서버로부터 수신한 메시지 처리
      console.log('수신한 메시지:', dat);
    });
    
    // 웹소켓 연결이 닫혔을 때 이벤트 핸들러
    socket.addEventListener('close', (event) => {
      console.log('WebSocket 연결이 닫혔습니다.', event);
    });
    
    // 웹소켓 에러 이벤트 핸들러
    socket.addEventListener('error', (event) => {
      console.error('WebSocket 에러가 발생하였습니다.', event);
    });
    
    // 메시지 전송 이벤트 핸들러
    const handleSendMessage = () => {
      // const socket = io(hoon);
      socket.send({'action':'sendOpinion', 'round':'1', 'opinion': 'hi'}); // 서버로 메시지 전송
      setMessage(''); // 메시지 입력 필드 초기화
    };

    functionRef.current = handleSendMessage;
    
    // 컴포넌트 언마운트 시 소켓 연결 해제
    return () => {
      socket.close();
    };
  }, []);


  // 컴포넌트 렌더링
  return (
    <div>
      {/* 채팅 UI 구현 */}
      <InGameNavBar/>
      <br></br>
      <input type="text" id='txt' className='rounded border-back-color border-solid border-x-4 border-y-4 px-1 py-1 mx-5' value={message} onChange={(e) => setMessage(e.target.value)} />
      <button className='text-md rounded bg-back-color text-white px-2 py-2' onClick={functionRef.current}>Send</button>
      {/* <button type='button' className='text-md rounded bg-back-color text-white px-2 py-2' onClick={this.websocketTest}>Web Socket Test Button</button> */}
      <br/>
      <div id='result' className='rounded text-md leading-none border-dotted border-x-4 border-y-4 border-back-color mx-5 my-5 px-1 py-1 inline-block'></div>
    </div>
  );
};

export default ChatComponent;


