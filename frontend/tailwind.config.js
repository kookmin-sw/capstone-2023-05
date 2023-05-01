const colors = require('tailwindcss/colors');

module.exports = {
    content: ["./src/**/*.{js,jsx,ts,tsx}","./"],
    theme:{
      extend:{
        colors:{
          'back-color' : '#29476E', // 남색 배경
          'background-color' : '#EAEAEA', // 회색 배경
          'sendBtn' : '#F4452F',
          'card-normal-A' : '#FCE6E2',
          'card-normal-B' : '#EEEFFF',
          'card-text-A' : '#F95150',
          'card-text-B' : '#322BDE',
        },
        backgroundImage: {
          'battleBar' : "url('./images/battleBar.png')",
          'like' : "url('./images/like.svg')",
          'star' : "url('./images/star.svg')",
          'bestLikesA' : "url('./images/bestLikesA.svg')",
          'bestLikesB' : "url('./images/bestLikesB.svg')",
        },
        backgroundSize:{
          'navBar' : '100%',
        },
        fontSize:{
          'nickname' :'1.5vh',
          'body' : '1vh',
        },
        height:{
          '7/8' : '87.5%',
          '1/8' : '12.5%',
          'card' : '17.2%',
          'opinion' : '74%',
          'likes' : '26%',
          'window-card' : '14.5vh',
          'time-bar' : '1%',
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
          'aboveBest':'5%',
          'navBar' : '21%',
          'aboveAds' : '7%',
          'opinion' : '11%',
        },
        margin:{
          'navBar' : '21%',
          'opinion' : '11%',
        },
        left:{
          '1/5' : '20%',
          '2/5' : '40%',
          '3/5' : '60%',
          '4/5' : '80%',
        },
      },
    },
  }