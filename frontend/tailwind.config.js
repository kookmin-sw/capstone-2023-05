const colors = require('tailwindcss/colors');

module.exports = {
    content: ["./src/**/*.{js,jsx,ts,tsx}","./"],
    theme:{
      extend:{
        colors:{
          'back-color' : '#29476E',
          'select-color' : '#58D3A0',
          'accent-color' : '#D35858'
        },
      },
    },
  }