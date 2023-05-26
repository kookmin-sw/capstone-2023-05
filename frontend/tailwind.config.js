const colors = require("tailwindcss/colors");

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./"],
  theme: {
    extend: {
      colors: {
        "back-color": "#29476E", // 남색 배경
        "background-color": "#EAEAEA", // 회색 배경
        sendBtn: "#F4452F",
        "card-normal-A": "#FCE6E2",
        "card-normal-B": "#EEEFFF",
        "card-text-A": "#F95150",
        "card-text-B": "#322BDE",
        "selected-A": "#F4452F",
        "selected-B": "#322BDE",
      },
      backgroundImage: {
        battleBar: "url('./images/battleBar.png')",
        lobbyBar: "url('./images/lobbyBar.png')",
        like: "url('./images/like.svg')",
        star: "url('./images/star.svg')",
        fire: "url('./images/fire.svg')",
        bestLikesA: "url('./images/bestLikesA.svg')",
        bestLikesB: "url('./images/bestLikesB.svg')",
        beforeStart: "url('./images/beforeStartBackground.svg')",
        players: "url('./images/person.svg')",
      },
      backgroundSize: {
        navBar: "100%",
      },
      backgroundSize: {
        navBar: "100%",
      },
      fontSize: {
        nickname: "1.5vh",
        body: "1vh",
      },
      height: {
        "7/8": "87.5%",
        "1/8": "12.5%",
        card: "17.2%",
        opinion: "74%",
        likes: "26%",
        "window-card": "14.5vh",
        "except-window-card": "85.5vh",
        "time-bar": "1%",
        "team-card": "38vh",
        "team-card-name": "22%",
        "team-card-img": "76.5%",
        "opinions-modal": "620px",
        "opinions-image": "220px",
        "opinions-team-name": "50px",
        "opinions-opinions": "350px",
      },
      width: {
        "7/8": "87.5%",
        "1/8": "12.5%",
        "7/10": "70%",
        "3/10": "30%",
        sendbtn: "23%",
        sendChat: "74%",
        card: "18.5%",
        "window-card": "12.34vw",
        "team-card": "23vw",
        "opinions-modal": "790px",
      },
      borderRadius: {
        card: "15px",
      },
      padding: {
        aboveBest: "5%",
        navBar: "21%",
        aboveAds: "7%",
        opinion: "11%",
        "modal-opinions": "8%",
      },
      margin: {
        "window-card": "14.5vh",
        navBar: "21%",
        opinion: "11%",
        "select-team": "23%",
      },
      left: {
        "1/5": "20%",
        "2/5": "40%",
        "3/5": "60%",
        "4/5": "80%",
      },
    },
  },
};
