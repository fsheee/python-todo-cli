/** @type {import('next').NextConfig} */
const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://todo-chatbot-backend:8002';

const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/api/:path*`,
      },
      {
        source: '/auth/:path*',
        destination: `${BACKEND_URL}/auth/:path*`,
      },
      {
        source: '/tasks/:path*',
        destination: `${BACKEND_URL}/tasks/:path*`,
      },
      {
        source: '/history/:path*',
        destination: `${BACKEND_URL}/history/:path*`,
      },
      {
        source: '/prompts/:path*',
        destination: `${BACKEND_URL}/prompts/:path*`,
      },
      {
        source: '/health',
        destination: `${BACKEND_URL}/health`,
      },
    ];
  },
}

module.exports = nextConfig
