/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/**/*.js"],
  theme: {
    extend: {
      colors: {
        // Modern Light Theme Palette
        primary: "#2196F3", // A vibrant blue for primary actions and branding
        "on-primary": "#FFFFFF", // White text on primary background
        secondary: "#FFC107", // An accent yellow for secondary actions
        "on-secondary": "#212121", // Dark text on secondary background
        background: "#F5F5F5", // Light gray background for the overall page
        surface: "#FFFFFF", // White for cards, dialogs, and elevated surfaces
        "on-surface": "#212121", // Dark text on surface
        "on-background": "#212121", // Dark text on background
        outline: "#BDBDBD", // Light gray for borders and dividers
        "on-outline": "#424242", // Darker text on outline elements
        hoverSurface: "#EEEEEE", // Slightly darker hover for surfaces
      },
    },
  },
  plugins: [],
};
