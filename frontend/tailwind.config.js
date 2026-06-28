/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        // The Problem Book — warm academic palette.
        // Oxblood is the single action color (The One Voice Rule, ≤10% of a screen).
        oxblood: {
          DEFAULT: "#8f3128",
          deep: "#79271f",
          tint: "#f4e0dc",
        },
        // Warm near-white paper, tinted toward oxblood's own hue (not generic cream).
        paper: "#fdfbfb",
        sunken: "#f7f1f0",
        edge: "#e8dcd9",
        // Warm ink ramp.
        ink: {
          DEFAULT: "#2b2622",
          strong: "#1c1815",
          muted: "#61584f",
          faint: "#9a8f86", // placeholder / disabled only — never body copy
        },
        // Math renders as the figure on the page: the darkest, heaviest element.
        mathink: "#261f1b",
        // Hints & difficulty — ochre, harmonized with oxblood.
        ochre: {
          DEFAULT: "#bd8431",
          tint: "#f8efdd",
          ink: "#79561f",
        },
        // Verified answers only (The Verified-Green Rule).
        verified: {
          DEFAULT: "#2f8d5d",
          tint: "#e4f3ea",
          edge: "#b9e0c8",
          ink: "#1d5e3c",
        },
        // Errors — vivid, kept distinct from muted oxblood, always icon-paired.
        danger: {
          DEFAULT: "#c0322c",
          tint: "#fbeae8",
          edge: "#f3c9c5",
          ink: "#8f211c",
        },
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(-4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        // Reduced-motion alternative: crossfade only, no positional movement.
        fadeInSoft: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        fadeIn: "fadeIn 0.25s cubic-bezier(0.22, 1, 0.36, 1) forwards",
      },
      transitionTimingFunction: {
        "out-quart": "cubic-bezier(0.25, 1, 0.5, 1)",
      },
    },
  },
  plugins: [],
};
