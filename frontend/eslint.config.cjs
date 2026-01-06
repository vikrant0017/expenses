// https://docs.expo.dev/guides/using-eslint/
const { defineConfig } = require("eslint/config");
const expoConfig = require("eslint-config-expo/flat");
const unusedImports = require("eslint-plugin-unused-imports");

module.exports = defineConfig([
  expoConfig,
  {
    ignores: ["dist/*"],
  },
  {
    plugins: {
      "unused-imports": unusedImports,
    },
    rules: {
      // Disable the base rule as it can report incorrect errors
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": "off",

      // Enable unused-imports rules
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],
    },
  },
]);
