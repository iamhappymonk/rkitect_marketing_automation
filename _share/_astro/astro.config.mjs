// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// Build serves under /v2 (Vercel rewrite maps /v2/* -> /_astro/dist/v2/*).
// Output goes to ./dist (inside the Astro project so node module resolution
// works at static-render time — moving it outside the project breaks Astro 5.1
// SSR bundling of `piccolore` and other deps).
export default defineConfig({
  site: 'https://rkitect.ai',
  base: '/v2',
  trailingSlash: 'never',
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
