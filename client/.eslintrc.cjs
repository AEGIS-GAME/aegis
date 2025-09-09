module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "@electron-toolkit/eslint-config-ts/recommended",
    "@electron-toolkit/eslint-config-prettier",
  ],
  rules: {
    "prettier/prettier": "error",
    eqeqeq: "error",
    "no-var": "error",
    "prefer-const": "warn",
    "no-global-assign": "error",
    "no-param-reassign": "warn",
    complexity: ["warn", { max: 16 }],
    curly: "error",
    "no-debugger": "error",
  },
}
