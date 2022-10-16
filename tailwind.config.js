/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./sopapp/templates/main/*.html", "./sopapp/templates/users/*.html", "./sopapp/routes/*.py", "./sopapp/static/assets/js/users.js"],
  theme: {
    extend: {
      animation:{
        dropdown: 'dropdown .4s forwards',
        dropup: 'dropup .4s forwards'
      },
      keyframes: {
        dropdown: {
          from: {
            transform: "scale-95",
            opacity: "0"
          },
          to: {
            transform: "scale-100",
            opacity: "100"
          },
          dropup: {
            from: {
              transform: "scale-100",
              opacity: "100"
            },
            to: {
              transform: "scale-95",
              opacity: "0"
            }
          }
        }
      }
    },
  },
  plugins: [],
}
