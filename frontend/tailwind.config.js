const colors = require('tailwindcss/colors');

module.exports = {
    content: ["./src/**/*.{js,jsx,ts,tsx}","./"],
    theme:{
      extend:{
        colors:{
          'back-color' : '#29476E', // 남색 배경
          'background-color' : '#EAEAEA', // 회색 배경
          'sendBtn' : '#F4452F',
          'card-normal' : '#FCE6E2',
          'card-text' : '#F95150',
        },
        backgroundImage: {
          'battleBar' : "url('./images/battleBar.png')",
          'like' : "url('./images/like.svg')",
          'star' : "url('./images/star.svg')",
        },
        fontSize:{
          'font' :'1vh',
        },
        height:{
          '7/8' : '87.5%',
          '1/8' : '12.5%',
          'card' : '17.2%',
          'opinion' : '74%',
          'likes' : '26%',
          'window-card' : '13.8vh',
        },
        width:{
          '7/8' : '87.5%',
          '1/8' : '12.5%',
          '7/10' : '70%',
          '3/10' : '30%',
          'sendbtn':'23%',
          'sendChat':'74%',
          'card' : '18.5%',
          'window-card':'12.34vw',
        },
        borderRadius:{
          'card': '15px'
        },
        padding:{
          'aboveBest':'8%'
        }
      },
    },
  }