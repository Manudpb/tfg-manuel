import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      minHeight:{
          'full': '75vh',
      },
      colors:{
        brandBlue:"#0075ff",
        brandBlueHover: "#0670a6",
      },
    },
  },
  plugins: [],
};
export default config;
