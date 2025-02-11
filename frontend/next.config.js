/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `http://localhost:8000/api/:path*`, // 代理到后端 API 服务器
      },
    ];
  },
  images: {
    domains: ['www.plantuml.com'],
  },
  async headers() {
    return [
      {
        source: '/drawio/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
        ],
      },
    ];
  },
};
module.exports = nextConfig;