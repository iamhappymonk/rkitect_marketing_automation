// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// Build directly into _share/v2/ so Vercel serves /v2/* natively.
// No vercel rewrites needed — pure static.
export default defineConfig({
  site: 'https://rkitect.ai',
  base: '/v2',
  trailingSlash: 'never',
  outDir: '../v2',
  build: {
    assets: 'assets',
    inlineStylesheets: 'auto',
  },
  integrations: [tailwind({ applyBaseStyles: false })],
  vite: {
    build: {
      cssMinify: 'lightningcss',
    },
  },
});
