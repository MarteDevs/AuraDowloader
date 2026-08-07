import js from '@eslint/js';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import prettier from 'eslint-config-prettier';
import globals from 'globals';

export default [
  {
    ignores: ['dist/**', 'node_modules/**', 'scripts/**', 'public/**', 'tests/setup.js'],
  },
  js.configs.recommended,
  {
    files: ['src/**/*.{js,jsx}', 'tests/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: { ...globals.browser, ...globals.node, ...globals.serviceworker },
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'jsx-a11y': jsxA11y,
    },
    settings: { react: { version: 'detect' } },
    rules: {
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      ...jsxA11y.configs.recommended.rules,
      'react/prop-types': 'off',
      'react/react-in-jsx-scope': 'off',
      'react/no-unescaped-entities': 'off',  // we use double quotes in Spanish text
      'jsx-a11y/no-autofocus': 'off',  // intentional on login
      'jsx-a11y/no-redundant-roles': 'error',  // keep this
      'jsx-a11y/click-events-have-key-events': 'off',  // modals have onClick on backdrop
      'jsx-a11y/no-static-element-interactions': 'off',  // same
      'jsx-a11y/no-noninteractive-element-interactions': ['error', {
        // Allow onClick on a <div> when it has role="dialog" + aria-modal.
        roles: ['dialog', 'alertdialog', 'menu', 'menubar', 'tablist'],
      }],
      'jsx-a11y/label-has-associated-control': ['error', { assert: 'either' }],
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      'no-empty': ['error', { allowEmptyCatch: true }],
    },
  },
  prettier,
];
